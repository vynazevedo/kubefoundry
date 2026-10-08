# Do zero ao primeiro diagnóstico

Você pode começar aqui sem conhecer Kubernetes. É normal não reconhecer todos os termos. A proposta é executar uma pequena mudança, observar o resultado e explicar o que aconteceu antes de avançar.

## Percurso

| Etapa | Você vai praticar | Pode avançar quando conseguir… |
| --- | --- | --- |
| 0 | [Preparar o computador](preparacao.md) | Confirmar que Docker e ferramentas funcionam |
| 1 | [Terminal, containers e YAML](terminal-containers-yaml.md) | Distinguir arquivo, imagem, container e processo |
| 2 | [Pod e Deployment](../tutorials/fundamentos-pods.md) | Explicar por que um Pod foi recriado e outro não |
| 3 | [Service e diagnóstico](../tutorials/fundamentos-rede.md) | Relacionar labels, seletores e endpoints |
| 4 | [Readiness e recuperação](../tutorials/fundamentos-readiness.md) | Distinguir processo em execução de aplicação pronta |
| 5 | [Helm](../tutorials/helm.md) e [GitOps](../tutorials/gitops.md) | Explicar quem declara e quem reconcilia o estado |

Não precisamos subir toda a plataforma para executar os fundamentos. `make up` prepara cluster, rede e políticas; `make image` disponibiliza nossa imagem. Depois disso, aplicamos os manifests manualmente no namespace `fundamentos`. Argo CD e PostgreSQL são opcionais e vêm depois.

## Um método para cada exercício

1. Leia o objetivo e preveja o resultado.
2. Execute um comando por vez.
3. Observe recursos, condições e eventos.
4. Explique a diferença entre previsão e resultado.
5. Faça o desafio sem olhar a solução.
6. Restaure o estado indicado no exercício.

## Para quem já tem experiência

Use os desafios como revisão e examine [tests/fundamentals.py](../../tests/fundamentals.py). Os testes verificam UIDs, endpoints prontos, resposta HTTP e recuperação. Não tratam apenas a aceitação de YAML como sucesso.

Essa trilha cobre uma primeira etapa de fundamentos. ConfigMaps, Secrets, volumes, autoscaling, telemetria e recuperação de dados terão laboratórios próprios. A [matriz de evolução](../architecture/trilhas-e-evolucao.md) distingue o que já é executável do que ainda está planejado.

[Voltar ao índice](../README.md)
