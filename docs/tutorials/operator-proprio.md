# Construa e observe um controller

## Para começar

Requer a imagem workbench disponível por `make advanced-up`.

```bash
make operator-test
```

O código em `operators/studyapp/` implementa um controller Go para `StudyApp`. Seu campo `spec.replicas` aceita de uma a três réplicas. O controller observa somente `kf-operator` e cria um Deployment com configuração restrita.

A suíte primeiro verifica que a API rejeita uma especificação ausente e réplicas fora do intervalo. Depois cria o recurso, observa prontidão, altera réplicas e aguarda `observedGeneration`. Em seguida remove o Deployment e verifica sua recriação com outro UID. Ao remover o StudyApp, valida a coleta do dependente por ownerReference. O RBAC impede criar Deployments fora do namespace.

## Experimente depois do teste

O teste remove o recurso de exemplo, mas deixa o controller instalado.

```bash
export KUBECONFIG="$PWD/.state/kubeconfig"
cat <<'YAML' | kubectl --context kind-kubefoundry apply -f -
apiVersion: learning.kubefoundry.io/v1alpha1
kind: StudyApp
metadata:
  name: minha-aplicacao
  namespace: kf-operator
spec:
  replicas: 2
YAML
kubectl --context kind-kubefoundry -n kf-operator get studyapps
kubectl --context kind-kubefoundry -n kf-operator get deployments
```

**Desafio**. Por que precisamos comparar `status.observedGeneration` com `metadata.generation` ao avaliar uma mudança?

<details>
<summary>Raciocínio</summary>

Um status pode descrever uma versão anterior da intenção. Comparar gerações ajuda a distinguir um resultado antigo de uma reconciliação da especificação atual.

</details>

## Para aprofundar

O controller usa consultas periódicas à API, TLS com a CA do cluster e releitura do token projetado. Recusa adotar Deployments cujo ownerReference não aponta para o StudyApp correspondente e usa resourceVersion em atualizações.

É um controller didático de escopo limitado. Reconcilia criação e quantidade de réplicas, não todas as possíveis alterações no template. Tem uma réplica e estratégia Recreate; não implementa eleição de líder, fila de eventos, backoff sofisticado, webhooks ou conversão de versões de CRD. Uma implementação de produção exigiria essas decisões e testes adicionais.

Não há finalizer porque não são geridos recursos externos. A limpeza dos dependentes Kubernetes usa garbage collection. Acrescentar um finalizer sem necessidade pode deixar exclusões presas.


[Voltar ao índice](../README.md)
