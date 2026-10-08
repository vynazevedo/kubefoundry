# Autoscaling com carga e recuperação

## Para começar

Requer `make advanced-up`. O Metrics Server fornece métricas de recursos para o HPA; Prometheus não é obrigatório neste exercício.

```bash
make autoscaling-test
```

O teste instala Metrics Server, aplica um HPA e espera métricas válidas. Em seguida gera carga limitada, durante 150 segundos, com quatro clientes. Ele exige que o Deployment ultrapasse uma réplica e retorne a uma após o término da carga. O máximo é três réplicas. Ao terminar com sucesso, remove o HPA do exercício.

## Observe durante a execução

```bash
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry -n kf-platform get hpa -w
```

Em outro terminal

```bash
kubectl --context kind-kubefoundry -n kf-platform top pods
kubectl --context kind-kubefoundry -n kf-platform get deployment workbench
```

**Desafio**. Explique por que ter três réplicas não significa automaticamente três vezes mais capacidade. Considere limites de CPU, banco, rede e dependências.

## Para aprofundar

A meta de CPU é expressa em relação aos requests declarados. Diminuir um request muda essa referência. O teste usa uma janela curta de estabilização para observar a redução em tempo de laboratório; uma aplicação real precisa de análise de comportamento e custos.

O Metrics Server usa `--kubelet-insecure-tls` somente no kind, cujos certificados de kubelet não atendem ao fluxo de validação usado aqui. Isso desativa a verificação do certificado naquela conexão. Não copie essa exceção para produção; configure certificados e confiança adequados. Ela não desativa TLS no restante do cluster.

Se o teste não aumentar réplicas, examine as condições do HPA e as métricas antes de aumentar a carga. O script tem prazo e limites para não gerar carga indefinida.


[Voltar ao índice](../README.md)
