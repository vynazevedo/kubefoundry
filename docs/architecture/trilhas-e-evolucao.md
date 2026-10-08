# Trilhas, evidências e evolução

O objetivo é servir quem está começando e quem já opera sistemas. Não chamamos uma capacidade de entregue apenas porque ela aparece em um diagrama.

| Nível | Disponível agora | Próximo aprofundamento |
| --- | --- | --- |
| Entrada | Preparação, terminal, containers, YAML, Pod e Deployment | Mais exercícios de configuração e armazenamento |
| Fundamentos | Service, seletores, readiness, falhas e recuperação | ConfigMaps, Secrets, PVC, StatefulSet e limites sob carga |
| Plataforma | Helm, Argo CD, Cilium, admissão, RBAC e operator de banco | Multi-time, identidade externa e promoção de ambientes |
| Operação | Verificações automatizadas e diagnóstico básico | Autoscaling, observabilidade, alertas e SLOs |
| Resiliência | Reconciliação de Pods e recuperação de configurações | Backup restaurado, RPO/RTO, falhas de nós e zonas |

## Critérios para as próximas entregas

- **Configuração e armazenamento**. Demonstrar alteração de configuração, comportamento após reinício e persistência conforme o tipo de volume. Secrets devem usar apenas dados fictícios.
- **Observabilidade**. Gerar tráfego e uma falha conhecida; encontrar evidência em métricas, logs e traces. Não basta instalar dashboards.
- **Autoscaling**. Medir carga, crescimento de réplicas e retorno ao patamar inicial, respeitando orçamento de recursos.
- **Múltiplos times**. Provar acesso permitido no próprio escopo e bloqueio no escopo de outro time, incluindo API e rede.
- **Recuperação de dados**. Restaurar um backup em ambiente separado e validar registros. Medir tempo e perda de dados.

## Relação com referências do mercado

O projeto usa material público para orientar temas e decisões. Não é um curso oficial da LinuxTips nem uma implementação das plataformas internas de Mercado Livre ou iFood.

A [ementa pública da LinuxTips](https://linuxtips.io/treinamento/descomplicando-o-kubernetes-codecon/) inclui uma cobertura mais ampla de fundamentos e operação. A [publicação sobre Fury](https://medium.com/mercadolibre-tech/kubernetes-at-mercado-libre-ec331bea1866) mostra uma plataforma interna que vai muito além de instalar Kubernetes. A [publicação do iFood sobre sua arquitetura de logística](https://institucional.ifood.com.br/inovacao/desenvolvimento-de-software-logistica-ifood/) descreve infraestrutura compartilhada como suporte a plataformas e equipes.

Essas referências ajudam a formular perguntas e objetivos. Não comprovam recomendação dessas organizações para este repositório ou para cada ferramenta escolhida.

[Voltar ao índice](../README.md)
