# Laboratório de PostgreSQL com operator

## Objetivo

Observar um controller especializado reconciliando um banco. Requer o cluster do quickstart e recursos adicionais disponíveis.

```bash
make database
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry -n cnpg-system get deployments
kubectl --context kind-kubefoundry -n databases get clusters.postgresql.cnpg.io
kubectl --context kind-kubefoundry -n databases get pods,pvc
```

O operator roda em `cnpg-system`. O recurso `study` e seus Pods ficam em `databases`. O script aguarda a condição `Ready` do recurso gerenciado.

## O que observar

Leia [platform/data/postgres.yaml](../../platform/data/postgres.yaml). `instances: 1` declara uma instância; `storage.size` solicita espaço por meio de um PVC. O operator transforma a intenção em recursos e acompanha seu estado.

```bash
kubectl --context kind-kubefoundry -n databases describe cluster study
kubectl --context kind-kubefoundry -n databases get events --sort-by=.lastTimestamp
```

Compare o que foi solicitado em `spec` com o que foi observado em `status`. Essa distinção é central para entender operators.

## Para aprofundar

Uma instância não oferece alta disponibilidade. O provisionamento local do kind não representa um serviço de armazenamento distribuído. A NetworkPolicy limita conexões de entrada, mas não é uma política completa de saída nem substitui autenticação PostgreSQL.

A aplicação demo não utiliza o banco. As credenciais são geradas como Secrets no cluster. Não imprima ou compartilhe seu conteúdo durante o exercício.

Não aumente réplicas e conclua que o sistema ficou resiliente sem testar falhas e recuperação. Backup externo, restauração para um instante específico e medição de perda de dados são exercícios futuros. `make down` destrói o ambiente e seus dados; só execute com dados descartáveis.

Referência. [documentação do CloudNativePG](https://cloudnative-pg.io/documentation/).


[Voltar ao índice](../README.md)
