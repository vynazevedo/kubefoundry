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
