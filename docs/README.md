# Aprenda Kubernetes construindo uma plataforma

Bem-vindo ao KubeFoundry. Este material foi feito para você entender o que está executando, experimentar com segurança e aprender a investigar quando algo não funciona.

Você não precisa conhecer todas as ferramentas antes de começar. Siga a trilha inicial e volte aos conceitos conforme aparecerem. Se já opera Kubernetes, vá direto à arquitetura, aos testes de segurança e aos limites do laboratório.

## Escolha sua trilha

| Quero… | Comece por… |
| --- | --- |
| Nunca usei Kubernetes | [Trilha do zero](getting-started/do-zero.md) |
| Planejar meu aprofundamento | [Trilhas e evolução](architecture/trilhas-e-evolucao.md) |
| Executar os perfis completos | [Plataforma completa](tutorials/plataforma-completa.md) |
| Configurar e persistir dados | [Configuração e storage](tutorials/configuracao-storage.md) |
| Investigar uma falha com telemetria | [Observabilidade](tutorials/observabilidade.md) |
| Medir escala sob carga | [Autoscaling](tutorials/autoscaling.md) |
| Isolar times | [Múltiplos times](security/multiplos-times.md) |
| Restaurar dados em outro banco | [Recuperação](tutorials/recuperacao.md) |
| Estudar HTTPS e entrega gradual | [Gateway e canary](tutorials/gateway-canary.md) |
| Rotacionar e verificar confiança | [Secrets e assinaturas](security/secrets-assinaturas.md) |
| Implementar reconciliação | [Operator próprio](tutorials/operator-proprio.md) |
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

O laboratório oferece uma trilha básica e perfis opcionais de configuração, armazenamento, telemetria, autoscaling, isolamento, restauração lógica, Gateway API, rotação de secrets, assinaturas e controller próprio. Cada tutorial distingue o comportamento testado das capacidades de produção que não estão configuradas.

## Contribua com o aprendizado

Encontrou uma explicação difícil, um comando que não funciona ou uma saída diferente? Abra uma issue com a etapa, versões e mensagem de erro, removendo credenciais. Melhorias de texto e exemplos de diagnóstico são contribuições tão úteis quanto código.
