Title: Demo de incorporações de conteúdo
Slug: demo-incorporacoes
Date: 2026-05-08
Lang: pt
Translation_key: embeds-demo
Status: hidden
Tags: Demo

Este post testa a extensão de etiquetas de conteúdo. Está permanentemente oculto do índice publicado — o seu único propósito é verificar que cada elemento é renderizado correctamente.

## Admonição (caixa de destaque)

!!! note "Uma nota"
    Esta é uma caixa `note` usando a extensão admonition do Python-Markdown. A cor da borda e do título acompanha o token `--accent`.

!!! warning "Um aviso"
    Esta é uma caixa `warning`. A cor é um vermelho quente fixo, legível nos temas claro e escuro.

!!! tip "Uma dica"
    As dicas usam o token `--accent-display`.

!!! danger "Perigo"
    Perigo usa um vermelho escuro. Usar com parcimónia.

## Figura com legenda

A imagem abaixo torna-se um elemento `<figure>` porque inclui um atributo de título no Markdown:

![Um quadrado branco — marcador de posição](assets/sample.png "Imagem de marcação: quadrado branco 16 × 16")

Uma imagem sem título renderiza como `<img>` simples:

![Um quadrado branco](assets/sample.png)

## Incorporação de YouTube

Big Buck Bunny da Blender Foundation (vídeo estável para testes):

[!youtube id="YE7VzlLtp-4"]

## Incorporação de iframe genérico

A página Wikipedia sobre jardins digitais:

[!iframe src="https://en.wikipedia.org/wiki/Digital_garden" title="Jardim digital — Wikipédia"]

## Bloco de código — as incorporações NÃO são expandidas aqui

O bloco abaixo deve renderizar como texto literal, não como iframe:

```
[!youtube id="YE7VzlLtp-4"]
```
