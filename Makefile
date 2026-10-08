SHELL := /bin/bash
.PHONY: tools up image deploy gitops database test verify check down security docs-check

tools:
	bash scripts/tools.sh
up:
	bash scripts/cluster.sh
image:
	bash scripts/image.sh
deploy:
	bash scripts/deploy.sh
gitops:
	bash scripts/gitops.sh
database:
	bash scripts/database.sh
test:
	cd apps/workbench && GOTOOLCHAIN=go1.27.1 go test -race ./... && GOTOOLCHAIN=go1.27.1 go vet ./...
	cd operators/studyapp && GOTOOLCHAIN=go1.27.1 go test -race ./... && GOTOOLCHAIN=go1.27.1 go vet ./...
	cd apps/demo && GOTOOLCHAIN=go1.27.1 go test -race ./... && GOTOOLCHAIN=go1.27.1 go vet ./...
check: test
	PATH="$(CURDIR)/.bin:$$PATH" python3 tests/static.py
verify:
	bash scripts/verify.sh
down:
	KUBECONFIG="$(CURDIR)/.state/kubeconfig" .bin/kind delete cluster --name kubefoundry

security:
	bash scripts/security.sh

docs-check:
	python3 scripts/check-docs.py

.PHONY: fundamentals-test
fundamentals-test:
	bash scripts/fundamentals-test.sh

.PHONY: workbench-image advanced-up configuration-test storage-test observability-up observability-test autoscaling-test tenancy-test recovery-test gateway-test canary-test secrets-test signatures-test operator-test advanced-security advanced-test
workbench-image:
	bash scripts/workbench-image.sh
advanced-up: workbench-image
	python3 scripts/advanced.py up
configuration-test:
	python3 scripts/advanced.py config
storage-test:
	python3 scripts/advanced.py storage
observability-up:
	python3 scripts/advanced.py telemetry-up
observability-test:
	python3 scripts/advanced.py telemetry-test
autoscaling-test:
	python3 scripts/advanced.py autoscaling
tenancy-test:
	python3 scripts/tenancy.py
recovery-test: database
	python3 scripts/recovery.py
gateway-test:
	bash scripts/gateway-up.sh
canary-test:
	python3 scripts/canary.py
secrets-test:
	bash scripts/secrets-up.sh
signatures-test:
	bash scripts/cosign-tools.sh
	bash scripts/signatures.sh
operator-test:
	bash scripts/operator-image.sh
advanced-security:
	bash scripts/advanced-security.sh
advanced-test:
	$(MAKE) advanced-up configuration-test storage-test tenancy-test observability-up observability-test autoscaling-test recovery-test gateway-test canary-test secrets-test operator-test signatures-test advanced-security
