# Aprenda Kubernetes construindo uma plataforma

Bem-vindo ao KubeFoundry. Este material foi feito para você entender o que está executando, experimentar com segurança e aprender a investigar quando algo não funciona.

Você não precisa conhecer todas as ferramentas antes de começar. Siga a trilha inicial e volte aos conceitos conforme aparecerem. Se já opera Kubernetes, vá direto à arquitetura, aos testes de segurança e aos limites do laboratório.

## Escolha sua trilha

| Quero… | Comece por… |
| --- | --- |
| Nunca usei Kubernetes | [Trilha do zero](getting-started/do-zero.md) |
| Planejar meu aprofundamento | [Trilhas e evolução](architecture/trilhas-e-evolucao.md) |
| Entender os nomes e as peças | [Conceitos essenciais](concepts/fundamentos.md) |
| Executar meu primeiro cluster | [Primeiros passos](getting-started/primeiro-cluster.md) |
| Entender as decisões técnicas | [Arquitetura e responsabilidades](architecture/plataforma.md) |
| Aprender a empacotar uma aplicação | [Laboratório de Helm](tutorials/helm.md) |
| Entregar mudanças pelo Git | [Laboratório de GitOps](tutorials/gitops.md) |
| Entender como provar uma proteção | [Segurança e testes](security/controles.md) |
| Trabalhar com bancos e operators | [Laboratório de PostgreSQL](tutorials/operators.md) |
| Manter e atualizar o ambiente | [Operação e evolução](operations/manutencao.md) |
| Resolver um erro | [Diagnóstico por sintoma](troubleshooting/diagnostico.md) |
| Conferir o que foi executado | [Evidências e capturas](assets/README.md) |

## Como usar os exemplos

Execute os comandos na raiz do repositório, salvo indicação contrária. Os exemplos de `kubectl` usam o kubeconfig do laboratório. Não copie comandos para um cluster de trabalho sem revisar contexto, namespace e efeito.

As seções **Para começar** explicam a intenção. As seções **Para aprofundar** discutem limites e decisões. Não são trilhas separadas de qualidade; são diferentes pontos de entrada.

O laboratório atual entrega aplicação Go, Helm, Cilium, políticas nativas, Argo CD e um perfil opcional de PostgreSQL. Gateway API, OpenTelemetry, assinatura de imagens, secrets externos e recuperação de desastres ainda são evolução planejada. Estudar conceitos de escala não significa que este cluster local reproduz a escala de uma grande empresa.

## Contribua com o aprendizado

Encontrou uma explicação difícil, um comando que não funciona ou uma saída diferente? Abra uma issue com a etapa, versões e mensagem de erro, removendo credenciais. Melhorias de texto e exemplos de diagnóstico são contribuições tão úteis quanto código.
