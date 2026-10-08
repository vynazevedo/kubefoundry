# Backup que realmente foi restaurado

## Objetivo

Provar a recuperação em outro banco, com dados conhecidos. O comando instala o perfil CloudNativePG se necessário.

```bash
make recovery-test
```

O teste cria dois clusters PostgreSQL temporários, identificados por um sufixo exclusivo. No primeiro, cria uma tabela fictícia, insere um registro e faz `pg_dump` em formato custom. Depois insere outro registro, posterior ao backup.

No segundo banco, executa `pg_restore`. A validação exige o primeiro registro e a ausência do segundo. Os dois clusters temporários são removidos ao encerrar. O banco `study` é usado como referência de configuração e seus dados não são modificados.

## Leia a evidência

```bash
cat .state/recovery-report.json
```

O relatório registra tamanho do backup, tempo de restauração com validação e tempo total do exercício. O dump sintético fica em `.state/` com permissão restrita. Esses arquivos não são versionados.

## Desafio

Se o segundo registro foi escrito antes de uma falha, por que não voltou? Qual mecanismo seria necessário para aproximar a recuperação de um instante posterior ao backup?

<details>
<summary>Raciocínio</summary>

O backup lógico representa os dados incluídos em sua execução. Ele não contém escritas posteriores. Arquivamento de WAL e recuperação para um ponto no tempo tratam outro cenário e precisam de configuração e testes próprios.

</details>

## Para aprofundar

RPO define a perda de dados aceitável. RTO define o tempo aceitável de recuperação. Os tempos medidos aqui são resultados locais, não metas garantidas para outro ambiente.

Este exercício testa backup lógico e restauração independente. Não configura PITR, armazenamento de backup fora do cluster, retenção, criptografia com gestão de chaves ou recuperação após perda de uma região. A réplica de um banco não substitui backup, e um arquivo de backup sem teste não prova recuperabilidade.


[Voltar ao índice](../README.md)
