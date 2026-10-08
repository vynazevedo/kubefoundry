# Readiness e recuperação

## Objetivo

Entender por que um processo pode estar executando e não estar pronto para receber tráfego. Requer o [Service funcionando](fundamentos-rede.md).

Readiness indica se o container está pronto para receber tráfego. Liveness pode provocar reinício quando sua verificação falha. Startup probes dão tempo à inicialização antes de outras verificações. Os manifests de fundamentos usam readiness e liveness; o chart da plataforma também inclui startup probe.

## Uma falha que preserva a aplicação

Edite `labs/fundamentos/deployment.yaml`. Na seção `readinessProbe`, troque somente o caminho `/readyz` por `/nao-existe`. Não altere o caminho da liveness.

```bash
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry apply -f labs/fundamentos/deployment.yaml
kubectl --context kind-kubefoundry -n fundamentos get pods -l app=primeiro-deployment
kubectl --context kind-kubefoundry -n fundamentos get events --sort-by=.lastTimestamp
```

O novo Pod poderá ficar `Running` e `0/1` pronto. A rota inexistente retorna erro à probe. Réplicas antigas saudáveis podem permanecer, pois o rolling update tenta preservar disponibilidade. Isso é comportamento esperado, não significa que a probe foi ignorada.

## Desafio

Por que observar apenas a fase `Running` é insuficiente? Por que um rollout pode ficar parado sem derrubar todas as réplicas anteriores?

<details>
<summary>Raciocínio e recuperação</summary>

A fase não resume todas as condições do Pod. A readiness influencia os destinos prontos do Service. Durante uma atualização gradual, limites de indisponibilidade impedem substituir todas as réplicas saudáveis por novas que não ficam prontas.

Restaure `/readyz` no arquivo e aplique novamente

```bash
kubectl --context kind-kubefoundry apply -f labs/fundamentos/deployment.yaml
kubectl --context kind-kubefoundry -n fundamentos rollout status deployment/primeiro-deployment --timeout=100s
kubectl --context kind-kubefoundry -n fundamentos exec primeiro-pod -- /demo probe http://primeiro-service:8080/healthz
```

</details>

## Validação automatizada e limpeza

```bash
make fundamentals-test
```

A suíte cria um namespace temporário com nome exclusivo, testa os manifests e solicita sua remoção ao terminar. Ela verifica substituição por UID, endpoints, HTTP, falhas e recuperação. Para testar a ausência total de endpoints com readiness inválida, o cenário automatizado substitui todas as réplicas do ambiente temporário. Isso é diferente da atualização gradual observada manualmente.

Para apagar somente os seus recursos de fundamentos, depois de confirmar que terminou os exercícios

```bash
kubectl --context kind-kubefoundry delete namespace fundamentos
```

Isso não remove `playground`, Argo CD ou PostgreSQL. Para destruir o cluster inteiro e seus dados, existe `make down`.

Agora siga para [Helm](helm.md), relacionando cada template com os recursos que acabou de manipular.

[Voltar ao índice](../README.md)
