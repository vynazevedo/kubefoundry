# Trilhas, evidências e evolução

O objetivo é servir quem está começando e quem já opera sistemas. Não chamamos uma capacidade de entregue apenas porque ela aparece em um diagrama.

| Nível | Disponível agora | Laboratório |
| --- | --- | --- |
| Entrada | Preparação, terminal, containers, YAML, Pod e Deployment | [Trilha inicial](../getting-started/do-zero.md) |
| Fundamentos | Service, readiness, ConfigMap, Secret e StatefulSet com PVC | [Configuração e storage](../tutorials/configuracao-storage.md) |
| Plataforma | GitOps, isolamento de times, Gateway API e controller próprio | [Perfis completos](../tutorials/plataforma-completa.md) |
| Operação | Métricas, logs, traces, alerta e HPA sob carga | [Observabilidade](../tutorials/observabilidade.md) |
| Resiliência | Backup lógico restaurado e canary com rollback | [Recuperação](../tutorials/recuperacao.md) |

## Limites que permanecem explícitos

Os perfis cobrem a trilha prática local. Não reproduzem infraestrutura de produção multi-região, SSO corporativo, PITR, backend durável de telemetria ou admissão de imagens assinadas. A documentação explica onde cada experimento termina para evitar transportar atalhos de laboratório para produção.

## Relação com referências do mercado

O projeto usa material público para orientar temas e decisões. Não é um curso oficial da LinuxTips nem uma implementação das plataformas internas de Mercado Livre ou iFood.

A [ementa pública da LinuxTips](https://linuxtips.io/treinamento/descomplicando-o-kubernetes-codecon/) inclui uma cobertura mais ampla de fundamentos e operação. A [publicação sobre Fury](https://medium.com/mercadolibre-tech/kubernetes-at-mercado-libre-ec331bea1866) mostra uma plataforma interna que vai muito além de instalar Kubernetes. A [publicação do iFood sobre sua arquitetura de logística](https://institucional.ifood.com.br/inovacao/desenvolvimento-de-software-logistica-ifood/) descreve infraestrutura compartilhada como suporte a plataformas e equipes.

Essas referências ajudam a formular perguntas e objetivos. Não comprovam recomendação dessas organizações para este repositório ou para cada ferramenta escolhida.

[Voltar ao índice](../README.md)
