---
title: Chronologie des projets
description: Les projets ajoutés au site, du plus récent au plus ancien.
permalink: /projets/chronologie/
---
{%- assign mois = "janvier,février,mars,avril,mai,juin,juillet,août,septembre,octobre,novembre,décembre" | split: "," -%}
{%- assign repos = site.data.repositories | sort: "added" | reverse -%}
{%- assign by_month = repos | group_by_exp: "r", "r.added | date: '%Y-%m'" %}

<ol class="timeline">
{%- for group in by_month %}
  {%- assign first = group.items | first %}
  {%- assign m = first.added | date: "%-m" | minus: 1 %}
  <li class="timeline__period">
    <h2 class="timeline__date"><time datetime="{{ group.name }}">{{ mois[m] | capitalize }} {{ first.added | date: "%Y" }}</time></h2>
    <ul class="timeline__items">
    {%- for repo in group.items %}
      {%- assign category = site.data.categories | where: "id", repo.category | first %}
      <li class="timeline__item">
        <time datetime="{{ repo.added | date: '%Y-%m-%d' }}">{{ repo.added | date: "%d" }}</time>
        <a href="{{ '/projets/' | relative_url }}#{{ repo.slug }}">{{ repo.name }}</a>
        <span class="chip chip--category">{{ category.emoji }} {{ category.label }}</span>
        <span class="timeline__desc">{{ repo.description }}</span>
      </li>
    {%- endfor %}
    </ul>
  </li>
{%- endfor %}
</ol>
