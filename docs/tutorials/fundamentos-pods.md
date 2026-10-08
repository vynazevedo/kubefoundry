# Pod e Deployment na prática

## Objetivo

Distinguir reinício de container, substituição de Pod e reconciliação de réplicas. Requer a [preparação](../getting-started/preparacao.md) concluída. Execute na raiz do projeto.

```bash
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry apply -f labs/fundamentos/namespace.yaml
kubectl --context kind-kubefoundry apply -f labs/fundamentos/network.yaml
kubectl --context kind-kubefoundry apply -f labs/fundamentos/pod.yaml
kubectl --context kind-kubefoundry -n fundamentos wait --for=condition=Ready pod/primeiro-pod --timeout=90s
kubectl --context kind-kubefoundry -n fundamentos get pods -o wide
```

O namespace mantém os recursos do exercício separados. Ele recebe Pod Security e as regras de admissão do laboratório. A política de rede permite comunicação HTTP entre Pods do mesmo namespace e DNS para o CoreDNS. Ela não representa isolamento entre pessoas autorizadas a criar Pods ali.

## O primeiro experimento

Registre o UID do Pod. Ele identifica essa instância do objeto.

```bash
kubectl --context kind-kubefoundry -n fundamentos get pod primeiro-pod -o jsonpath='{.metadata.uid}'
kubectl --context kind-kubefoundry -n fundamentos delete pod primeiro-pod
kubectl --context kind-kubefoundry -n fundamentos get pods
```

O Pod não deve reaparecer por conta própria. Não há um Deployment declarando que ele precisa existir. Isso é diferente de um container reiniciar dentro de um Pod que continua existindo.

## Declare duas réplicas

```bash
kubectl --context kind-kubefoundry apply -f labs/fundamentos/deployment.yaml
kubectl --context kind-kubefoundry -n fundamentos rollout status deployment/primeiro-deployment --timeout=100s
kubectl --context kind-kubefoundry -n fundamentos get pods -l app=primeiro-deployment
```

Escolha um dos nomes retornados. Copie o nome para uma variável e apague apenas esse Pod, neste namespace de estudo

```bash
# Troque o valor abaixo pelo nome que apareceu no seu terminal.
pod_do_exercicio='COLE_O_NOME_AQUI'
kubectl --context kind-kubefoundry -n fundamentos delete pod "$pod_do_exercicio"
kubectl --context kind-kubefoundry -n fundamentos get pods -l app=primeiro-deployment -w
```

Observe a criação de um substituto e encerre a observação com Ctrl+C. Confirme duas réplicas prontas. O novo objeto tem outro UID. O Deployment coordena ReplicaSets, que mantêm os Pods necessários.

## Critério de aprendizado

Sem olhar a explicação, descreva por que o primeiro Pod não reapareceu e o segundo foi substituído. Depois abra o manifest e identifique a quantidade de réplicas e os labels usados pelo seletor.

<details>
<summary>Pista</summary>

O manifest de um Pod isolado não cria um controller de réplicas. O Deployment mantém uma intenção persistente, que continua existindo quando um de seus Pods é removido.

</details>

Recrie o Pod isolado, que será nosso cliente no próximo exercício

```bash
kubectl --context kind-kubefoundry apply -f labs/fundamentos/pod.yaml
kubectl --context kind-kubefoundry -n fundamentos wait --for=condition=Ready pod/primeiro-pod --timeout=90s
```

Próxima etapa. [Service e diagnóstico](fundamentos-rede.md). Referência. [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).

[Voltar ao índice](../README.md)
