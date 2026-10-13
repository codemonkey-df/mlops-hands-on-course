# Course task runner. `make help` lists targets.
SHELL := /bin/bash
LXC_IP ?= $(shell hostname -I | awk '{print $$1}')
export LXC_IP
CLUSTER := mlops

.PHONY: help docs docs-build cluster-up cluster-down cluster-stop cluster-start cluster-status \
        lint fmt typecheck test precommit urls

help: ## Show this help
	@grep -hE '^[a-zA-Z0-9_%-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-22s\033[0m %s\n",$$1,$$2}'

# ---------- course site ----------
docs: ## Serve the course site on http://$(LXC_IP):8000 (live reload)
	uv run mkdocs serve -a 0.0.0.0:8000 --livereload

docs-build: ## Strict build of the site (fails on broken snippets/links)
	uv run mkdocs build --strict

# ---------- cluster ----------
platform/k3d/cluster.yaml: platform/k3d/cluster.yaml.tpl
	envsubst '$${LXC_IP}' < $< > $@

cluster-up: platform/k3d/cluster.yaml ## Create the k3d cluster
	k3d cluster create --config platform/k3d/cluster.yaml
	kubectl wait --for=condition=Ready nodes --all --timeout=120s

cluster-down: ## Delete the cluster (ALL data inside is lost)
	k3d cluster delete $(CLUSTER)

cluster-stop: ## Stop node containers, keep state (frees RAM)
	k3d cluster stop $(CLUSTER)

cluster-start: ## Start a stopped cluster
	k3d cluster start $(CLUSTER)

cluster-status: ## Nodes, pods and resource usage
	kubectl get nodes -o wide && kubectl get pods -A && kubectl top nodes

urls: ## Print the web UIs of the course
	@echo "Course site : http://$(LXC_IP):8000"
	@kubectl get ingress -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}http://{.spec.rules[0].host}:8080{"\n"}{end}' 2>/dev/null || true

# ---------- exercises ----------
check-%: ## Run break/fix verifiers: make check-m01 [BUG=bug02]
	@scripts/check.sh $* $(BUG)

verify-%: ## (maintainer) broken must fail, solution must pass: make verify-m01
	@scripts/verify-exercises.sh $*

catchup-%: ## Copy verified reference of a module + deploy it: make catchup-m03
	@scripts/catchup.sh $*

# ---------- python quality gate ----------
lint: ## ruff lint
	uv run ruff check .
fmt: ## ruff format
	uv run ruff format .
typecheck: ## mypy
	uv run mypy src/
test: ## pytest
	uv run pytest -q
precommit: lint fmt typecheck test ## Everything that must pass before a commit
