# Laboratório de Helm

## Objetivo

Entender como valores viram manifests, antes de alterar o cluster. Requer `make tools`; a aplicação em execução só é necessária para a segunda parte.

```bash
.bin/helm lint charts/demo --strict
.bin/helm template demo charts/demo --namespace playground
.bin/helm template demo charts/demo --namespace playground --set replicaCount=3
```

Compare o campo `spec.replicas` do Deployment nas duas renderizações. Renderizar é gerar texto; ainda não muda o cluster.

## Experimente uma entrada inválida

```bash
.bin/helm template demo charts/demo --set replicaCount=0
```

Este comando deve falhar porque o schema exige pelo menos uma réplica. A falha aqui é esperada. O schema ajuda a detectar entradas inadequadas antes de chegar à API.

## Aplique uma mudança local

Antes de habilitar GitOps, altere `replicaCount` em `charts/demo/values.yaml` para `3` e execute

```bash
make deploy
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry -n playground get deployment demo
```

Espere três réplicas prontas. Volte o valor para `2` e execute `make deploy` novamente para encerrar o exercício.

## Para aprofundar

`make deploy` usa `helm template` seguido de `kubectl apply`. Portanto, não cria uma release consultável por `helm list`. Isso aproxima o fluxo local da renderização usada pelo Argo CD e evita dois gerenciadores concorrentes para os mesmos objetos.

Depois de habilitar GitOps, use mudanças no Git. O self-heal pode desfazer alterações locais. Rollback deve considerar o estado desejado registrado no Git, e não somente a revisão de um Deployment.

O chart aceita digest de imagem, mas o quickstart usa uma imagem local com tag. Não confunda essa conveniência de laboratório com verificação de procedência de imagens.

Referência. [estrutura de charts Helm](https://helm.sh/docs/topics/charts/).


[Voltar ao índice](../README.md)
