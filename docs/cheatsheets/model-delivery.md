# Model delivery paths

Two valid on-prem patterns appear in this course. They are not one unfinished
design: churn serving **bakes** the model into the image; LLM serving **pulls**
weights when the pod starts.

| Workload | Artifact source | Who builds | How cluster gets it |
|----------|-----------------|------------|---------------------|
| Churn Bento | MLflow `@champion` | CI (import → bento build → Harbor) | Image tag in GitOps |
| vLLM mock | Fake weights in MinIO | N/A (chart + initContainer) | initContainer copy |

## Gotcha

**Dagster does not push serving images.** Dagster trains and may move
`@champion`. CI imports that alias, builds `churn-bento`, pushes to Harbor, and
commits the tag. Argo CD rolls the Deployment. Until CI runs, pods keep the old
baked weights even if MLflow already points at a newer champion.

## Where this shows up

- [M6 — Releasing a new model](../modules/m06-bentoml.md#releasing-a-new-model)
- [M7 — Gitea CI + Harbor](../modules/m07-ci-harbor.md) (builds and pushes the Bento image)
- [M9 — Weights from object storage](../modules/m09-llm-serving.md#2-foundations)
- [M11 — Capstone sequence](../modules/m11-capstone.md#1-problem-to-solve) (drift → promote → CI → sync)
