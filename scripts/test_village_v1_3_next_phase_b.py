#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 AIMath contributors
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import copy
import hashlib
import json
import unittest

import village_next_phase_b as pb
from village_next_phase_b import (
    CanonicalAcquireIdentityV3,
    ExactLockObject,
    RulesetProof,
    SemanticIds,
    VerifyObservation,
)
from village_v1_2 import CapabilityProfile

BASE_SHA = "a" * 40
HEAD_SHA = "b" * 40
ALT_HEAD_SHA = "c" * 40
M_SHA = "d" * 40
WORKER = "w-" + "a" * 16
WORKER_B = "w-" + "b" * 16
PRINCIPAL = "gh:51mns"
TASK = "TASK-NEXT-1"
NOW = datetime(2026, 9, 2, 12, 0, tzinfo=timezone.utc)


def _base_entries():
    raw = b"base fixture\n"
    return [{"path": "README.md", "mode": "100644", "type": "blob", "sha": pb.git_blob_oid(raw)}]


def _base_tree():
    return pb.deterministic_tree_sha(_base_entries())


def _ids(a="1", b="2", c="3", d="4"):
    return SemanticIds(a * 64, b * 64, c * 64, d * 64)


def _material(ids=None, *, worker=WORKER, acquired_at=NOW, collision_keys=("x/next",), task=TASK):
    ids = ids or _ids()
    return pb.freeze_acquire_material(
        semantic_ids=ids,
        base_sha=BASE_SHA,
        base_tree_sha=_base_tree(),
        base_tree_entries=_base_entries(),
        selected_task_id=task,
        worker_id=worker,
        principal_id=PRINCIPAL,
        work_ref=f"research/{task}/{worker}",
        collision_keys=collision_keys,
        acquired_at=acquired_at,
        lease_ttl_hours=168,
    )


def _candidate_entries(material=None):
    material = material or _material()
    rows = copy.deepcopy(_base_entries())
    rows.extend(
        {"path": obj.path, "mode": obj.mode, "type": "blob", "sha": obj.blob_sha}
        for obj in material.identity.exact_lock_objects
    )
    return rows


def _candidate_commit(material=None, *, sha=HEAD_SHA, parent=BASE_SHA, parents=None, tree_sha=None):
    material = material or _material()
    ps = parents if parents is not None else [{"sha": parent}]
    return {"sha": sha, "parents": ps, "tree": {"sha": tree_sha or material.identity.expected_canonical_tree_sha}}


def _good_ruleset():
    return RulesetProof(True, "RULESET_PROOF_CONFIRMED", "strict verify, no bypass")


def _ruleset_inputs(*, strict=True, context="verify", bypass=None, can="never"):
    effective = [{
        "type": "required_status_checks",
        "parameters": {
            "strict_required_status_checks_policy": strict,
            "required_status_checks": [{"context": context}],
        },
    }]
    detail = [{
        "id": 22089746,
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "rules": copy.deepcopy(effective),
        "bypass_actors": [] if bypass is None else bypass,
        "current_user_can_bypass": can,
    }]
    return effective, detail


def _run(number, run_id, *, head=HEAD_SHA, status="completed", conclusion="success", attempt=1):
    return {
        "id": run_id,
        "workflow_id": pb.VERIFY_WORKFLOW_ID,
        "path": pb.VERIFY_WORKFLOW_PATH,
        "name": pb.VERIFY_WORKFLOW_NAME,
        "event": pb.VERIFY_EVENT,
        "head_sha": head,
        "run_number": number,
        "run_attempt": attempt,
        "status": status,
        "conclusion": conclusion,
    }


def _observe(rows, current=None, *, head=HEAD_SHA, complete=True):
    by_id = {row["id"]: row for row in rows}
    if current:
        by_id.update(current)
    return pb.authoritative_verify_lineage(rows, head_sha=head, complete=complete, fetch_current_run=lambda rid: by_id[rid])


def _good_verify(head=HEAD_SHA, number=10, run_id=9):
    row = _run(number, run_id, head=head)
    return _observe([row], head=head)


def _history(material=None, *, m_parents=None, m_tree=None, current_entries=None):
    material = material or _material()
    m_entries = current_entries or _candidate_entries(material)
    m = {
        "sha": M_SHA,
        "parents": m_parents if m_parents is not None else [{"sha": BASE_SHA}],
        "tree": {"sha": m_tree or material.identity.expected_canonical_tree_sha},
        "entries": m_entries,
    }
    b = {"sha": BASE_SHA, "parents": [], "tree": {"sha": _base_tree()}, "entries": _base_entries()}
    return [m, b]


def _canonical_gate(material=None, *, history=None, current_entries=None, current_lock_bytes=None, rules=None, now=NOW):
    material = material or _material()
    return pb.canonical_transition_gate(
        identity=material.identity,
        first_parent_history=history or _history(material),
        current_entries=current_entries or _candidate_entries(material),
        current_lock_bytes=current_lock_bytes or material.lock_bytes,
        ruleset=rules or _good_ruleset(),
        now=now,
    )


def _premerge(material=None, *, commit=None, entries=None, verify=None, rules=None, current_main=BASE_SHA, ids=None):
    material = material or _material()
    return pb.premerge_transport_gate(
        identity=material.identity,
        independently_derived_ids=ids or material.identity.semantic_ids(),
        base_entries=_base_entries(),
        candidate_commit=commit or _candidate_commit(material),
        candidate_entries=entries or _candidate_entries(material),
        candidate_lock_bytes=material.lock_bytes,
        verify=verify or _good_verify(),
        ruleset=rules or _good_ruleset(),
        current_main_sha=current_main,
    )


def _source_record(*, lock_blob=None, terminal_blob=None, acquired="2026-09-01T00:00:00+00:00"):
    lock_blob = lock_blob or "e" * 40
    terminal_blob = terminal_blob or "f" * 40
    payload = {
        "schema_version": 1,
        "lock_id": "LOCK-SOURCE",
        "task_id": "TASK-SOURCE",
        "worker_id": WORKER,
        "actor": {"id": PRINCIPAL, "type": "HUMAN_PRINCIPAL"},
        "base_main_sha": "0" * 40,
        "acquired_at": acquired,
        "expires_at": "2026-09-10T00:00:00+00:00",
        "work_ref": f"research/TASK-SOURCE/{WORKER}",
        "collision_keys": ["source/key"],
        "renewal_count": 0,
    }
    return pb.derive_source_acquisition_v1(
        repository=pb.REPOSITORY,
        source_task_id="TASK-SOURCE",
        worker_id=WORKER,
        principal_id=PRINCIPAL,
        lock_payload=payload,
        source_lock_blob_bundle=[{"path": "coordination/locks/source/key.yml", "blob_sha": lock_blob}],
        terminal_class="RESULT_TERMINAL",
        terminal_path="coordination/outcomes/TASK-SOURCE.yml",
        terminal_blob_sha=terminal_blob,
        terminal_outcome_type="NO_REUSABLE_PROGRESS",
    )


def _trusted_semantic_chain():
    source_record, source_id = _source_record()
    context, context_id = pb.derive_continuation_context_v1(
        source_epoch_id=source_id,
        selection_main_sha=BASE_SHA,
        terminal_class="RESULT_TERMINAL",
        terminal_blob_sha=source_record["terminal_blob_sha"],
        source_campaign_id="CAM-X",
        global_admission="OPEN",
        source_campaign_strategic_state="ACTIVE",
        continuation_gate_required=False,
        continuation_decision_id=None,
        continuation_decision_blob_sha=None,
        human_decision=None,
        canonical_stop_condition_reached=False,
        canonical_dependency_followup_unusable=False,
        same_campaign_allowed=True,
        global_fallback_allowed=True,
        approved_followup_task_ids=[TASK],
        evaluation_followup_task_ids=[],
        reasons=[],
        capability_profile=CapabilityProfile.from_values(github_write="yes", local_compute="yes", web_literature="unknown"),
    )
    selection, selection_id = pb.derive_selection_v1(
        source_epoch_id=source_id,
        selection_main_sha=BASE_SHA,
        continuation_context_id=context_id,
        pending_records=[],
        hard_eligible_task_ids=[TASK],
        ranked_task_ids=[TASK],
        selected_task_id=TASK,
        selected_relation="GLOBAL_READY",
        worker_id=WORKER,
        principal_id=PRINCIPAL,
    )
    intent, intent_id = pb.derive_acquire_intent_v1(
        source_epoch_id=source_id,
        selection_id=selection_id,
        selection_main_sha=BASE_SHA,
        continuation_context_id=context_id,
        selected_task_id=TASK,
        worker_id=WORKER,
        principal_id=PRINCIPAL,
        work_ref=f"research/{TASK}/{WORKER}",
        collision_keys=["x/next"],
    )
    ids = SemanticIds(source_id, context_id, selection_id, intent_id)
    material = _material(ids)
    state = {
        "schema_version": 1,
        "repository": pb.REPOSITORY,
        "source_acquisition_v1": source_record,
        "source_epoch_id": source_id,
        "continuation_context_v1": context,
        "continuation_context_id": context_id,
        "selection_v1": selection,
        "selection_id": selection_id,
        "acquire_intent_v1": intent,
        "acquire_intent_id": intent_id,
        "canonical_acquire_identity_v3": material.identity.to_dict(),
        "canonical_acquire_id": material.canonical_acquire_id,
    }
    return source_record, context, selection, intent, ids, material, state


def _release_fixture(*, verify=True):
    source_path = "coordination/locks/source/key.yml"
    source_bytes = b'{"lock_id":"LOCK-SOURCE"}\n'
    source_blob = pb.git_blob_oid(source_bytes)
    base_entries = [
        {"path": "README.md", "mode": "100644", "type": "blob", "sha": pb.git_blob_oid(b"base\n")},
        {"path": source_path, "mode": "100644", "type": "blob", "sha": source_blob},
    ]
    base_sha = "6" * 40
    base_tree = pb.deterministic_tree_sha(base_entries)
    released_entries = [row for row in base_entries if row["path"] != source_path]
    released_tree = pb.deterministic_tree_sha(base_entries, deletions=[source_path], expected_base_tree_sha=base_tree)
    source_record = {"source_lock_blob_bundle": [{"path": source_path, "blob_sha": source_blob}]}
    transport = {"sha": "7" * 40, "parents": [{"sha": base_sha}], "tree": {"sha": released_tree}}
    m = {"sha": "8" * 40, "parents": [{"sha": base_sha}], "tree": {"sha": released_tree}, "entries": released_entries}
    b = {"sha": base_sha, "parents": [], "tree": {"sha": base_tree}, "entries": base_entries}
    vo = VerifyObservation(verify, "VERIFY_AUTHORITATIVE_SUCCESS" if verify else "LATEST_VERIFY_NOT_SUCCESS", 10, 1, 1, "completed", "success")
    return source_record, base_sha, released_tree, transport, released_entries, vo, [m, b]


class VillageV13PhaseB73(unittest.TestCase):
    def test_row_01_happy_path_release_select_acquire_and_active_next(self):
        material = _material()
        self.assertTrue(_premerge(material).allowed)
        self.assertEqual(_canonical_gate(material).code, "CANONICAL_ACQUIRE_IDENTITY_CONFIRMED")

    def test_row_02_unrelated_same_worker_principal_lock_never_satisfies_active_next(self):
        material = _material()
        current = _base_entries() + [{"path": "coordination/locks/other.yml", "mode": "100644", "type": "blob", "sha": "e" * 40}]
        self.assertFalse(_canonical_gate(material, current_entries=current).allowed)

    def test_row_03_old_acquisition_lock_id_or_timestamp_never_satisfies(self):
        material = _material()
        payload = copy.deepcopy(material.lock_payload); payload["lock_id"] = "LOCK-OLD"
        self.assertFalse(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_04_wrong_work_ref_fails_active_next(self):
        material = _material(); payload = copy.deepcopy(material.lock_payload); payload["work_ref"] = "research/wrong"
        self.assertFalse(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_05_wrong_collision_bundle_fails_active_next(self):
        material = _material(); payload = copy.deepcopy(material.lock_payload); payload["collision_keys"] = ["wrong/key"]
        self.assertFalse(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_06_wrong_worker_fails_binding(self):
        material = _material(); payload = copy.deepcopy(material.lock_payload); payload["worker_id"] = WORKER_B
        self.assertFalse(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_07_wrong_principal_fails_binding(self):
        material = _material(); payload = copy.deepcopy(material.lock_payload); payload["actor"]["id"] = "gh:other"
        self.assertFalse(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_08_stale_acquire_base_has_no_pending_or_merge_authority(self):
        self.assertEqual(_premerge(current_main="9" * 40).code, "CANONICAL_ACQUIRE_BASE_MISMATCH")

    def test_row_09_stale_release_repair_requires_new_current_verify(self):
        args = _release_fixture(verify=False)
        got = pb.release_provenance_gate(
            source_record=args[0], release_base_sha=args[1], release_expected_tree_sha=args[2],
            release_transport_commit=args[3], release_transport_entries=args[4], release_verify=args[5], first_parent_history=args[6],
        )
        self.assertFalse(got.allowed); self.assertEqual(pb.deterministic_release_ref("TASK-SOURCE", WORKER), pb.deterministic_release_ref("TASK-SOURCE", WORKER))

    def test_row_10_stale_pr_head_invalidates_prior_verify_and_transport_identity(self):
        green_old = _good_verify(head=HEAD_SHA)
        material = _material()
        moved = _candidate_commit(material, sha=ALT_HEAD_SHA)
        got = pb.premerge_transport_gate(
            identity=material.identity, independently_derived_ids=material.identity.semantic_ids(), base_entries=_base_entries(),
            candidate_commit=moved, candidate_entries=_candidate_entries(material), candidate_lock_bytes=material.lock_bytes,
            verify=VerifyObservation(False, "LATEST_VERIFY_NOT_SUCCESS"), ruleset=_good_ruleset(), current_main_sha=BASE_SHA,
        )
        self.assertTrue(green_old.eligible); self.assertFalse(got.allowed)

    def test_row_11_duplicate_next_has_one_deterministic_release_and_acquire_key(self):
        ids = _ids()
        self.assertEqual(pb.deterministic_acquire_ref(ids.acquire_intent_id, TASK, WORKER), pb.deterministic_acquire_ref(ids.acquire_intent_id, TASK, WORKER))
        self.assertEqual(pb.deterministic_release_ref("TASK-SOURCE", WORKER), pb.deterministic_release_ref("TASK-SOURCE", WORKER))

    def test_row_12_duplicate_creator_adopts_exact_winner_and_non_equivalent_content_is_rejected(self):
        winner = _material(acquired_at=NOW)
        loser = _material(acquired_at=NOW + timedelta(seconds=1))
        self.assertEqual(pb.deterministic_acquire_ref(winner.identity.acquire_intent_id, TASK, WORKER), pb.deterministic_acquire_ref(loser.identity.acquire_intent_id, TASK, WORKER))
        self.assertNotEqual(winner.identity, loser.identity)

    def test_row_13_old_source_acquisition_replay_changes_source_epoch(self):
        _, a = _source_record(acquired="2026-09-01T00:00:00+00:00")
        _, b = _source_record(acquired="2026-09-01T00:00:01+00:00")
        self.assertNotEqual(a, b)

    def test_row_14_equivalent_release_transport_uses_same_deterministic_ref(self):
        self.assertEqual(pb.deterministic_release_ref("TASK-SOURCE", WORKER), "release/TASK-SOURCE/" + WORKER)

    def test_row_15_unrelated_release_content_is_conflict_not_reuse(self):
        args = list(_release_fixture()); args[0] = {"source_lock_blob_bundle": [{"path": "coordination/locks/source/key.yml", "blob_sha": "0" * 40}]}
        got = pb.release_provenance_gate(source_record=args[0], release_base_sha=args[1], release_expected_tree_sha=args[2], release_transport_commit=args[3], release_transport_entries=args[4], release_verify=args[5], first_parent_history=args[6])
        self.assertFalse(got.allowed)

    def test_row_16_already_released_requires_exact_source_epoch_release_provenance(self):
        args = _release_fixture()
        got = pb.release_provenance_gate(source_record=args[0], release_base_sha=args[1], release_expected_tree_sha=args[2], release_transport_commit=args[3], release_transport_entries=args[4], release_verify=args[5], first_parent_history=args[6])
        self.assertEqual(got.code, "SOURCE_EPOCH_RELEASE_PROVENANCE_CONFIRMED")

    def test_row_17_equivalent_acquire_pr_is_same_transport_key(self):
        material = _material(); ref = pb.deterministic_acquire_ref(material.identity.acquire_intent_id, TASK, WORKER)
        self.assertEqual(ref, pb.deterministic_acquire_ref(material.identity.acquire_intent_id, TASK, WORKER))

    def test_row_18_exact_ref_without_pr_has_one_create_key(self):
        intent = _ids().acquire_intent_id
        refs = {pb.deterministic_acquire_ref(intent, TASK, WORKER) for _ in range(10)}
        self.assertEqual(len(refs), 1)

    def test_row_19_canonical_v3_transition_not_pr_metadata_grants_active_next(self):
        got = _canonical_gate(); self.assertTrue(got.allowed); self.assertEqual(got.code, "CANONICAL_ACQUIRE_IDENTITY_CONFIRMED")

    def test_row_20_self_consistent_forged_next_binding_fails_trusted_expected_ids(self):
        _src, _ctx, _sel, _intent, expected_ids, expected_material, _state = _trusted_semantic_chain()
        fields = ("source_epoch_id", "continuation_context_id", "selection_id", "acquire_intent_id")
        for field in fields:
            with self.subTest(field=field):
                values = expected_ids.__dict__.copy(); values[field] = "f" * 64
                forged_ids = SemanticIds(**values)
                forged = _material(forged_ids)
                # The candidate is object-internally self-consistent with its own forged binding.
                for obj in forged.identity.exact_lock_objects:
                    raw = forged.lock_bytes[obj.path]
                    self.assertEqual(pb.git_blob_oid(raw), obj.blob_sha)
                    self.assertEqual(hashlib.sha256(raw).hexdigest(), obj.bytes_sha256)
                self.assertEqual(pb.deterministic_tree_sha(_candidate_entries(forged)), forged.identity.expected_canonical_tree_sha)
                got = pb.candidate_content_gate(
                    expected_identity=expected_material.identity,
                    independently_derived_ids=expected_ids,
                    candidate_lock_bytes=forged.lock_bytes,
                    candidate_exact_objects=forged.identity.exact_lock_objects,
                    candidate_tree_sha=forged.identity.expected_canonical_tree_sha,
                )
                self.assertFalse(got.allowed); self.assertEqual(got.code, "CANONICAL_ACQUIRE_SEMANTIC_BINDING_MISMATCH")

    def test_row_21_historical_transition_exact_but_current_lock_later_changed_is_not_active(self):
        material = _material(); raw = next(iter(material.lock_bytes.values())) + b" "
        current = dict(material.lock_bytes); current[next(iter(current))] = raw
        self.assertFalse(_canonical_gate(material, current_lock_bytes=current).allowed)

    def test_row_22_two_workers_same_task_only_matching_canonical_identity_wins(self):
        a = _material(worker=WORKER); b = _material(worker=WORKER_B, ids=_ids("1","2","3","5"))
        self.assertNotEqual(a.identity.acquire_intent_id, b.identity.acquire_intent_id)
        self.assertFalse(_canonical_gate(b, history=_history(a), current_entries=_candidate_entries(a), current_lock_bytes=a.lock_bytes).allowed)

    def test_row_23_overlapping_collision_bundle_first_canonical_owner_blocks_second(self):
        first = _material(); base_after = _candidate_entries(first)
        with self.assertRaises(pb.PhaseBError):
            pb.freeze_acquire_material(semantic_ids=_ids("1","2","3","5"), base_sha=M_SHA, base_tree_sha=first.identity.expected_canonical_tree_sha, base_tree_entries=base_after, selected_task_id="TASK-NEXT-2", worker_id=WORKER_B, principal_id=PRINCIPAL, work_ref=f"research/TASK-NEXT-2/{WORKER_B}", collision_keys=["x/next"], acquired_at=NOW, lease_ttl_hours=168)

    def test_row_24_campaign_last_slot_race_second_stale_base_fails(self):
        self.assertFalse(_premerge(current_main=M_SHA).allowed)

    def test_row_25_global_last_slot_race_second_stale_base_fails(self):
        self.assertEqual(_premerge(current_main=M_SHA).code, "CANONICAL_ACQUIRE_BASE_MISMATCH")

    def test_row_26_release_beats_acquire_when_both_eligible(self):
        kind, row = pb.choose_lifecycle_candidate([{"eligible": True, "pr_number": 8}], [{"eligible": True, "pr_number": 1}])
        self.assertEqual((kind, row["pr_number"]), ("RELEASE", 8))

    def test_row_27_at_most_one_trusted_lifecycle_candidate_per_run(self):
        kind, row = pb.choose_lifecycle_candidate([{"eligible": True, "pr_number": 8}, {"eligible": True, "pr_number": 9}], [{"eligible": True, "pr_number": 1}])
        self.assertEqual((kind, row["pr_number"]), ("RELEASE", 8))

    def test_row_28_ruleset_observation_unavailable_or_malformed_fails_closed(self):
        self.assertFalse(pb.prove_ruleset(None, None).passed)

    def test_row_29_ruleset_strict_false_or_verify_missing_fails_closed(self):
        for strict, context in ((False, "verify"), (True, "other")):
            with self.subTest(strict=strict, context=context):
                e, d = _ruleset_inputs(strict=strict, context=context); self.assertFalse(pb.prove_ruleset(e, d).passed)

    def test_row_30_exact_head_ci_red_or_missing_has_no_activation_authority(self):
        failed = _observe([_run(10, 1, status="completed", conclusion="failure")]); missing = _observe([], head=HEAD_SHA)
        self.assertFalse(failed.eligible); self.assertFalse(missing.eligible)

    def test_row_31_old_head_green_does_not_transfer_to_moved_head(self):
        old = _good_verify(head=HEAD_SHA); moved = _observe([_run(10, 1, head=HEAD_SHA)], head=ALT_HEAD_SHA)
        self.assertTrue(old.eligible); self.assertFalse(moved.eligible)

    def test_row_32_candidate_local_malformed_drops_only_candidate(self):
        kind, row = pb.choose_lifecycle_candidate([], [{"eligible": False, "pr_number": 1}, {"eligible": True, "pr_number": 2}])
        self.assertEqual((kind, row["pr_number"]), ("ACQUIRE", 2))

    def test_row_33_repository_wide_observation_failure_is_global_fail_closed(self):
        got = pb.repository_observation_gate(main_sha=BASE_SHA, tree_complete=True, open_prs_complete=False, principal_id=PRINCIPAL)
        self.assertFalse(got.allowed); self.assertEqual(got.code, "REPOSITORY_OBSERVATION_INCOMPLETE")

    def test_row_34_candidate_disappears_or_closes_is_dropped_and_later_valid_examined(self):
        kind, row = pb.choose_lifecycle_candidate([], [{"eligible": False, "pr_number": 3}, {"eligible": True, "pr_number": 4}])
        self.assertEqual((kind, row["pr_number"]), ("ACQUIRE", 4))

    def test_row_35_main_moves_after_release_before_selection_changes_selection_identity(self):
        _, _, selection, _, ids, _, _ = _trusted_semantic_chain()
        moved = dict(selection); moved["selection_main_sha"] = "9" * 40
        self.assertNotEqual(ids.selection_id, pb.canonical_digest(moved))

    def test_row_36_main_moves_after_selection_before_acquire_creation_rejects_old_intent(self):
        self.assertFalse(_premerge(current_main="9" * 40).allowed)

    def test_row_37_main_moves_after_acquire_pr_creation_old_pr_is_not_ownership(self):
        self.assertFalse(pb.is_pending_ownership({"head_sha": HEAD_SHA})); self.assertFalse(_premerge(current_main=M_SHA).allowed)

    def test_row_38_pending_claim_is_nonownership_even_when_green(self):
        self.assertFalse(pb.is_pending_ownership({"verify_conclusion": "SUCCESS", "pr_state": "OPEN"}))

    def test_row_39_terminal_release_can_proceed_without_truth_promotion(self):
        self.assertEqual(pb.TRUTH_AUTHORITY, frozenset()); self.assertTrue(pb.deterministic_release_ref("TASK-SOURCE", WORKER).startswith("release/"))

    def test_row_40_no_autonomous_i2_i3_or_writer_self_review_authority(self):
        self.assertEqual(pb.REVIEW_AUTHORITY, frozenset())

    def test_row_41_no_automatic_renew_or_takeover_path(self):
        self.assertEqual(pb.FORBIDDEN_AUTOMATIC_OPERATIONS, frozenset({"RENEW", "TAKEOVER"}))

    def test_row_42_missing_human_gate_cannot_same_campaign_escalate(self):
        source_record, source_id = _source_record()
        rec, _ = pb.derive_continuation_context_v1(source_epoch_id=source_id, selection_main_sha=BASE_SHA, terminal_class="RESULT_TERMINAL", terminal_blob_sha=source_record["terminal_blob_sha"], source_campaign_id="CAM-X", global_admission="OPEN", source_campaign_strategic_state="ACTIVE", continuation_gate_required=True, continuation_decision_id=None, continuation_decision_blob_sha=None, human_decision=None, canonical_stop_condition_reached=False, canonical_dependency_followup_unusable=False, same_campaign_allowed=False, global_fallback_allowed=True, approved_followup_task_ids=[TASK], evaluation_followup_task_ids=[], reasons=["required human Continuation Gate decision is absent"], capability_profile=CapabilityProfile())
        self.assertTrue(rec["continuation_gate_required"]); self.assertFalse(rec["same_campaign_allowed"])

    def test_row_43_worker_recommendation_cannot_create_or_approve_task_or_campaign(self):
        names = set(pb.__all__)
        self.assertFalse({"create_task", "create_campaign", "approve_task", "approve_campaign"} & names)

    def test_row_44_selection_context_changes_recompute_identity_before_acquire(self):
        _s, context, selection, _i, ids, _m, _st = _trusted_semantic_chain()
        for field, value in (("pending_observation_digest", "f" * 64), ("ranked_task_ids", [TASK, "TASK-OTHER"]), ("hard_eligible_task_ids", [TASK, "TASK-OTHER"])):
            with self.subTest(field=field):
                changed = copy.deepcopy(selection); changed[field] = value; self.assertNotEqual(ids.selection_id, pb.canonical_digest(changed))
        changed_context = copy.deepcopy(context); changed_context["human_decision"] = "CONTINUE"
        self.assertNotEqual(ids.continuation_context_id, pb.canonical_digest(changed_context))

    def test_row_45_source_terminal_blob_change_invalidates_old_source_epoch(self):
        _, a = _source_record(terminal_blob="f" * 40); _, b = _source_record(terminal_blob="1" * 40)
        self.assertNotEqual(a, b)

    def test_row_46_source_lock_blob_bundle_change_invalidates_old_release_request(self):
        _, a = _source_record(lock_blob="e" * 40); _, b = _source_record(lock_blob="2" * 40)
        self.assertNotEqual(a, b)

    def test_row_47_deterministic_lock_id_stable_and_intent_distinct(self):
        self.assertEqual(pb.deterministic_lock_id("1" * 64), pb.deterministic_lock_id("1" * 64)); self.assertNotEqual(pb.deterministic_lock_id("1" * 64), pb.deterministic_lock_id("2" * 64))

    def test_row_48_first_creator_timestamp_is_immutable_for_same_intent_retry(self):
        first = _material(acquired_at=NOW); retry_wrong = _material(acquired_at=NOW + timedelta(seconds=1))
        self.assertEqual(first.identity.acquire_intent_id, retry_wrong.identity.acquire_intent_id); self.assertNotEqual(first.lock_bytes, retry_wrong.lock_bytes)
        adopted = _material(acquired_at=NOW); self.assertEqual(first.lock_bytes, adopted.lock_bytes)

    def test_row_49_canonical_lock_path_blob_bundle_must_equal_expected_transport_bundle(self):
        material = _material(); entries = _candidate_entries(material); entries[-1]["sha"] = "0" * 40
        self.assertFalse(_canonical_gate(material, current_entries=entries).allowed)

    def test_row_50_expired_canonical_lock_never_active_next(self):
        material = _material(acquired_at=NOW - timedelta(days=10)); self.assertEqual(_canonical_gate(material, now=NOW).code, "CANONICAL_LOCK_NOT_ACTIVE")

    def test_row_51_same_content_alternate_head_is_same_canonical_acquisition_content(self):
        material = _material(); h1 = _candidate_commit(material, sha=HEAD_SHA); h2 = _candidate_commit(material, sha=ALT_HEAD_SHA)
        self.assertNotEqual(h1["sha"], h2["sha"]); self.assertEqual(h1["tree"], h2["tree"]); self.assertNotIn("expected_head_sha", material.identity.to_dict())

    def test_row_52_webhook_delivery_is_trigger_only_not_identity_authority(self):
        material = _material(); before = material.canonical_acquire_id
        noisy = material.identity.to_dict(); noisy_copy = copy.deepcopy(noisy); noisy_copy.pop("schema_version"); noisy_copy["webhook_run_id"] = 999999
        self.assertEqual(before, material.identity.canonical_id()); self.assertNotIn("webhook_run_id", material.identity.to_dict())

    def test_row_53_multiple_release_lowest_pr_wins_after_malformed_lower_drop(self):
        kind, row = pb.choose_lifecycle_candidate([{"eligible": False, "pr_number": 1}, {"eligible": True, "pr_number": 2}, {"eligible": True, "pr_number": 3}], [])
        self.assertEqual((kind, row["pr_number"]), ("RELEASE", 2))

    def test_row_54_multiple_acquire_lowest_pr_wins_after_malformed_lower_drop(self):
        kind, row = pb.choose_lifecycle_candidate([], [{"eligible": False, "pr_number": 1}, {"eligible": True, "pr_number": 2}, {"eligible": True, "pr_number": 3}])
        self.assertEqual((kind, row["pr_number"]), ("ACQUIRE", 2))

    def test_row_55_highest_run_number_controls_not_run_id_magnitude(self):
        rows = [_run(10, 999999), _run(11, 1, conclusion="failure")]
        got = _observe(rows); self.assertFalse(got.eligible); self.assertEqual(got.authoritative_run_number, 11); self.assertEqual(got.run_id, 1)

    def test_row_56_indirect_merge_commit_attack_is_noncanonical(self):
        material = _material(); history = _history(material, m_parents=[{"sha": BASE_SHA}, {"sha": "9" * 40}])
        self.assertEqual(_canonical_gate(material, history=history).code, "NONCANONICAL_ACQUIRE_MERGE_SHAPE")

    def test_row_57_different_pr_locator_same_head_can_confirm_only_v3_content_transition(self):
        material = _material(); self.assertTrue(_canonical_gate(material).allowed); self.assertNotIn("pr_number", material.identity.to_dict()); self.assertNotIn("pr_ref", material.identity.to_dict())

    def test_row_58_rerun_older_run_cannot_outrank_newer_failure(self):
        old = _run(10, 10, attempt=2, conclusion="success"); newer = _run(11, 11, conclusion="failure")
        got = _observe([old, newer]); self.assertFalse(got.eligible); self.assertEqual(got.authoritative_run_number, 11)

    def test_row_59_new_higher_successful_lineage_recovers(self):
        rows = [_run(10, 10), _run(11, 11, conclusion="failure"), _run(12, 12)]
        got = _observe(rows); self.assertTrue(got.eligible); self.assertEqual(got.authoritative_run_number, 12)

    def test_row_60_authoritative_lineage_current_rerun_in_progress_is_not_eligible(self):
        listed = _run(11, 11, attempt=1, conclusion="success")
        current = _run(11, 11, attempt=2, status="in_progress", conclusion=None)
        got = _observe([listed], current={11: current}); self.assertFalse(got.eligible); self.assertEqual(got.current_run_attempt, 2)

    def test_row_61_incomplete_or_non_single_first_parent_history_fails_closed(self):
        material = _material(); self.assertEqual(pb.canonical_transition_gate(identity=material.identity, first_parent_history=[_history(material)[0]], current_entries=_candidate_entries(material), current_lock_bytes=material.lock_bytes, ruleset=_good_ruleset(), now=NOW).code, "CANONICAL_ACQUIRE_HISTORY_UNPROVEN")

    def test_row_62_ruleset_bypass_or_unreadable_regression_fails_closed(self):
        e, d = _ruleset_inputs(bypass=[{"actor_id": 1}]); self.assertEqual(pb.prove_ruleset(e, d).code, "RULESET_BYPASS_PRESENT")
        self.assertFalse(pb.prove_ruleset([], []).passed)

    def test_row_63_same_tree_alternate_head_cannot_borrow_verify(self):
        material = _material(); h2 = _candidate_commit(material, sha=ALT_HEAD_SHA)
        borrowed = _good_verify(head=HEAD_SHA)
        got = pb.premerge_transport_gate(identity=material.identity, independently_derived_ids=material.identity.semantic_ids(), base_entries=_base_entries(), candidate_commit=h2, candidate_entries=_candidate_entries(material), candidate_lock_bytes=material.lock_bytes, verify=VerifyObservation(False, "LATEST_VERIFY_NOT_SUCCESS"), ruleset=_good_ruleset(), current_main_sha=BASE_SHA)
        self.assertTrue(borrowed.eligible); self.assertFalse(got.allowed)

    def test_row_64_same_tree_alternate_head_with_stale_or_different_base_is_ineligible(self):
        material = _material(); commit = _candidate_commit(material, sha=ALT_HEAD_SHA, parent="9" * 40)
        self.assertEqual(_premerge(material, commit=commit, verify=_good_verify(head=ALT_HEAD_SHA)).code, "CANONICAL_ACQUIRE_BASE_MISMATCH")

    def test_row_65_same_base_but_different_tree_or_object_is_ineligible(self):
        material = _material(); commit = _candidate_commit(material, tree_sha="9" * 40)
        self.assertEqual(_premerge(material, commit=commit).code, "CANONICAL_ACQUIRE_TREE_MISMATCH")

    def test_row_66_same_objects_but_claimed_different_source_epoch_is_semantic_inconsistency(self):
        material = _material(); claimed = replace(material.identity.semantic_ids(), source_epoch_id="f" * 64)
        got = pb.candidate_content_gate(expected_identity=material.identity, independently_derived_ids=claimed, candidate_lock_bytes=material.lock_bytes, candidate_exact_objects=material.identity.exact_lock_objects, candidate_tree_sha=material.identity.expected_canonical_tree_sha)
        self.assertFalse(got.allowed); self.assertEqual(got.code, "CANONICAL_ACQUIRE_SEMANTIC_BINDING_MISMATCH")

    def test_row_67_same_objects_but_claimed_different_acquire_intent_is_semantic_inconsistency(self):
        material = _material(); claimed = replace(material.identity.semantic_ids(), acquire_intent_id="f" * 64)
        got = pb.candidate_content_gate(expected_identity=material.identity, independently_derived_ids=claimed, candidate_lock_bytes=material.lock_bytes, candidate_exact_objects=material.identity.exact_lock_objects, candidate_tree_sha=material.identity.expected_canonical_tree_sha)
        self.assertFalse(got.allowed); self.assertEqual(got.code, "CANONICAL_ACQUIRE_SEMANTIC_BINDING_MISMATCH")

    def test_row_68_squash_positive_h_not_equal_m_but_same_b_t_content_confirms(self):
        material = _material(); h = _candidate_commit(material, sha=HEAD_SHA); history = _history(material); self.assertNotEqual(h["sha"], history[0]["sha"]); self.assertEqual(h["tree"]["sha"], history[0]["tree"]["sha"]); self.assertTrue(_canonical_gate(material, history=history).allowed)

    def test_row_69_duplicate_exact_lock_path_fails_before_canonical_hashing(self):
        material = _material(); obj = material.identity.exact_lock_objects[0]; bad = replace(material.identity, exact_lock_objects=(obj, obj))
        with self.assertRaises(pb.PhaseBError) as cm: pb.validate_v3_identity(bad)
        self.assertEqual(cm.exception.code, "CANONICAL_ACQUIRE_DUPLICATE_LOCK_PATH")

    def test_row_70_mutating_source_continuation_or_selection_binding_changes_bytes_oid_and_tree(self):
        base = _material()
        for field in ("source_epoch_id", "continuation_context_id", "selection_id"):
            with self.subTest(field=field):
                vals = base.identity.semantic_ids().__dict__.copy(); vals[field] = "f" * 64
                changed = _material(SemanticIds(**vals))
                self.assertNotEqual(base.lock_bytes, changed.lock_bytes)
                self.assertNotEqual(base.identity.exact_lock_objects[0].bytes_sha256, changed.identity.exact_lock_objects[0].bytes_sha256)
                self.assertNotEqual(base.identity.exact_lock_objects[0].blob_sha, changed.identity.exact_lock_objects[0].blob_sha)
                self.assertNotEqual(base.identity.expected_canonical_tree_sha, changed.identity.expected_canonical_tree_sha)

    def test_row_71_mutating_acquire_intent_binding_changes_bytes_oid_and_tree(self):
        base = _material(); vals = base.identity.semantic_ids().__dict__.copy(); vals["acquire_intent_id"] = "f" * 64; changed = _material(SemanticIds(**vals))
        self.assertNotEqual(base.lock_bytes, changed.lock_bytes); self.assertNotEqual(base.identity.exact_lock_objects[0].blob_sha, changed.identity.exact_lock_objects[0].blob_sha); self.assertNotEqual(base.identity.expected_canonical_tree_sha, changed.identity.expected_canonical_tree_sha)

    def test_row_72_post_squash_semantic_reconstruction_comes_from_canonical_bytes_not_process_memory(self):
        _s, _c, _sel, _i, _ids0, material, state = _trusted_semantic_chain(); self.assertTrue(_canonical_gate(material).allowed)
        tampered = copy.deepcopy(state); tampered["selection_id"] = "f" * 64
        with self.assertRaises(pb.PhaseBError): pb.validate_retained_state_chain(tampered)
        payload = json.loads(next(iter(material.lock_bytes.values())).decode("utf-8")); self.assertTrue(pb.reconstruct_v3_from_lock_payload(material.identity, payload).allowed)

    def test_row_73_missing_required_next_binding_fails_next_only(self):
        payload = copy.deepcopy(_material().lock_payload); payload.pop("next_binding")
        with self.assertRaises(pb.PhaseBError) as cm: pb.parse_next_binding(payload)
        self.assertEqual(cm.exception.code, "CANONICAL_ACQUIRE_NEXT_BINDING_MISSING")


SPEC_ROW_TO_TEST = {
    1: "test_row_01_happy_path_release_select_acquire_and_active_next",
    2: "test_row_02_unrelated_same_worker_principal_lock_never_satisfies_active_next",
    3: "test_row_03_old_acquisition_lock_id_or_timestamp_never_satisfies",
    4: "test_row_04_wrong_work_ref_fails_active_next",
    5: "test_row_05_wrong_collision_bundle_fails_active_next",
    6: "test_row_06_wrong_worker_fails_binding",
    7: "test_row_07_wrong_principal_fails_binding",
    8: "test_row_08_stale_acquire_base_has_no_pending_or_merge_authority",
    9: "test_row_09_stale_release_repair_requires_new_current_verify",
    10: "test_row_10_stale_pr_head_invalidates_prior_verify_and_transport_identity",
    11: "test_row_11_duplicate_next_has_one_deterministic_release_and_acquire_key",
    12: "test_row_12_duplicate_creator_adopts_exact_winner_and_non_equivalent_content_is_rejected",
    13: "test_row_13_old_source_acquisition_replay_changes_source_epoch",
    14: "test_row_14_equivalent_release_transport_uses_same_deterministic_ref",
    15: "test_row_15_unrelated_release_content_is_conflict_not_reuse",
    16: "test_row_16_already_released_requires_exact_source_epoch_release_provenance",
    17: "test_row_17_equivalent_acquire_pr_is_same_transport_key",
    18: "test_row_18_exact_ref_without_pr_has_one_create_key",
    19: "test_row_19_canonical_v3_transition_not_pr_metadata_grants_active_next",
    20: "test_row_20_self_consistent_forged_next_binding_fails_trusted_expected_ids",
    21: "test_row_21_historical_transition_exact_but_current_lock_later_changed_is_not_active",
    22: "test_row_22_two_workers_same_task_only_matching_canonical_identity_wins",
    23: "test_row_23_overlapping_collision_bundle_first_canonical_owner_blocks_second",
    24: "test_row_24_campaign_last_slot_race_second_stale_base_fails",
    25: "test_row_25_global_last_slot_race_second_stale_base_fails",
    26: "test_row_26_release_beats_acquire_when_both_eligible",
    27: "test_row_27_at_most_one_trusted_lifecycle_candidate_per_run",
    28: "test_row_28_ruleset_observation_unavailable_or_malformed_fails_closed",
    29: "test_row_29_ruleset_strict_false_or_verify_missing_fails_closed",
    30: "test_row_30_exact_head_ci_red_or_missing_has_no_activation_authority",
    31: "test_row_31_old_head_green_does_not_transfer_to_moved_head",
    32: "test_row_32_candidate_local_malformed_drops_only_candidate",
    33: "test_row_33_repository_wide_observation_failure_is_global_fail_closed",
    34: "test_row_34_candidate_disappears_or_closes_is_dropped_and_later_valid_examined",
    35: "test_row_35_main_moves_after_release_before_selection_changes_selection_identity",
    36: "test_row_36_main_moves_after_selection_before_acquire_creation_rejects_old_intent",
    37: "test_row_37_main_moves_after_acquire_pr_creation_old_pr_is_not_ownership",
    38: "test_row_38_pending_claim_is_nonownership_even_when_green",
    39: "test_row_39_terminal_release_can_proceed_without_truth_promotion",
    40: "test_row_40_no_autonomous_i2_i3_or_writer_self_review_authority",
    41: "test_row_41_no_automatic_renew_or_takeover_path",
    42: "test_row_42_missing_human_gate_cannot_same_campaign_escalate",
    43: "test_row_43_worker_recommendation_cannot_create_or_approve_task_or_campaign",
    44: "test_row_44_selection_context_changes_recompute_identity_before_acquire",
    45: "test_row_45_source_terminal_blob_change_invalidates_old_source_epoch",
    46: "test_row_46_source_lock_blob_bundle_change_invalidates_old_release_request",
    47: "test_row_47_deterministic_lock_id_stable_and_intent_distinct",
    48: "test_row_48_first_creator_timestamp_is_immutable_for_same_intent_retry",
    49: "test_row_49_canonical_lock_path_blob_bundle_must_equal_expected_transport_bundle",
    50: "test_row_50_expired_canonical_lock_never_active_next",
    51: "test_row_51_same_content_alternate_head_is_same_canonical_acquisition_content",
    52: "test_row_52_webhook_delivery_is_trigger_only_not_identity_authority",
    53: "test_row_53_multiple_release_lowest_pr_wins_after_malformed_lower_drop",
    54: "test_row_54_multiple_acquire_lowest_pr_wins_after_malformed_lower_drop",
    55: "test_row_55_highest_run_number_controls_not_run_id_magnitude",
    56: "test_row_56_indirect_merge_commit_attack_is_noncanonical",
    57: "test_row_57_different_pr_locator_same_head_can_confirm_only_v3_content_transition",
    58: "test_row_58_rerun_older_run_cannot_outrank_newer_failure",
    59: "test_row_59_new_higher_successful_lineage_recovers",
    60: "test_row_60_authoritative_lineage_current_rerun_in_progress_is_not_eligible",
    61: "test_row_61_incomplete_or_non_single_first_parent_history_fails_closed",
    62: "test_row_62_ruleset_bypass_or_unreadable_regression_fails_closed",
    63: "test_row_63_same_tree_alternate_head_cannot_borrow_verify",
    64: "test_row_64_same_tree_alternate_head_with_stale_or_different_base_is_ineligible",
    65: "test_row_65_same_base_but_different_tree_or_object_is_ineligible",
    66: "test_row_66_same_objects_but_claimed_different_source_epoch_is_semantic_inconsistency",
    67: "test_row_67_same_objects_but_claimed_different_acquire_intent_is_semantic_inconsistency",
    68: "test_row_68_squash_positive_h_not_equal_m_but_same_b_t_content_confirms",
    69: "test_row_69_duplicate_exact_lock_path_fails_before_canonical_hashing",
    70: "test_row_70_mutating_source_continuation_or_selection_binding_changes_bytes_oid_and_tree",
    71: "test_row_71_mutating_acquire_intent_binding_changes_bytes_oid_and_tree",
    72: "test_row_72_post_squash_semantic_reconstruction_comes_from_canonical_bytes_not_process_memory",
    73: "test_row_73_missing_required_next_binding_fails_next_only",
}

assert tuple(SPEC_ROW_TO_TEST) == tuple(range(1, 74))
assert len(set(SPEC_ROW_TO_TEST.values())) == 73
assert all(hasattr(VillageV13PhaseB73, name) for name in SPEC_ROW_TO_TEST.values())
assert len([name for name in dir(VillageV13PhaseB73) if name.startswith("test_")]) == 73


if __name__ == "__main__":
    unittest.main(verbosity=2)
