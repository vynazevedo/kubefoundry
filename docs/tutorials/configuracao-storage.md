# Configuração, Secrets e persistência

## Para começar

Requer `make advanced-up`. Abra `labs/advanced/base.json`: JSON também é aceito pela API Kubernetes. Os objetos estão em uma List para facilitar sua aplicação conjunta.

```bash
make configuration-test
make storage-test
export KUBECONFIG="$PWD/.state/kubeconfig"
kubectl --context kind-kubefoundry -n kf-platform get configmaps,secrets,statefulsets,pvc
```

O teste de configuração muda uma mensagem não sensível e observa dois caminhos. O arquivo de ConfigMap montado é atualizado sem recriar o Pod, após a propagação. A variável de ambiente preserva o valor recebido na criação do processo e muda após reiniciar o Deployment.

O teste de Secret apenas confirma que o arquivo está disponível e não vazio. O conteúdo é uma credencial fictícia. Nem o endpoint `/secret-status` nem o teste imprimem o valor.

## Experimente

```bash
kubectl --context kind-kubefoundry -n kf-platform exec deployment/workbench -- /workbench get http://127.0.0.1:8080/config
kubectl --context kind-kubefoundry -n kf-platform get statefulset storage
kubectl --context kind-kubefoundry -n kf-platform get pvc
```

**Desafio**. Por que o StatefulSet mantém o nome `storage-0`, mas o UID do Pod muda durante o teste? Qual recurso mantém o dado?

<details>
<summary>Raciocínio</summary>

O nome estável representa a posição no StatefulSet. Uma nova instância de Pod recebe outro UID. O PVC associado é reutilizado, permitindo que o novo Pod monte os dados existentes. Isso não depende de o processo anterior continuar existindo.

</details>

## Para aprofundar

A aplicação usa `emptyDir` no Deployment e PVC no StatefulSet. `emptyDir` acompanha a vida do Pod; não é um armazenamento persistente entre Pods. O experimento de persistência usa exclusivamente o StatefulSet.

O volume local do kind não replica dados entre máquinas. Recriar o Pod neste cluster não equivale a sobreviver à perda do computador, da zona ou do cluster. O [exercício de recuperação](recuperacao.md) usa outro mecanismo para demonstrar uma restauração independente.

A aplicação limita escritas HTTP a 1 KiB e mantém a raiz somente para leitura. A escrita é feita no volume `/data`. Não utilize dados pessoais ou credenciais reais nos exercícios.


[Voltar ao índice](../README.md)
