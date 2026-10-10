---
title: Projets
description: Dépôts et projets validés — enseignement, recherche, web et outils.
permalink: /projets/
---
{%- assign repos = site.data.repositories | sort: "added" | reverse -%}
{%- assign total = repos | size -%}
{%- assign languages = repos | where_exp: "r", "r.language" | group_by: "language" | sort: "size" | reverse -%}
{%- assign categories = repos | group_by: "category" | sort: "size" | reverse -%}
{%- assign last = repos | first -%}

## En chiffres

<div class="stats">
  <div class="stat"><span class="stat__value">{{ total }}</span><span class="stat__label">projets</span></div>
  <div class="stat"><span class="stat__value">{{ languages | size }}</span><span class="stat__label">langages</span></div>
  <div class="stat"><span class="stat__value">{{ categories | size }}</span><span class="stat__label">catégories</span></div>
  <div class="stat"><span class="stat__value stat__value--small">{% include date-fr.html date=last.added %}</span><span class="stat__label">dernier ajout</span></div>
</div>

<div class="stats-detail">
  <section aria-labelledby="stats-langages">
    <h3 id="stats-langages">Langages</h3>
    <ul class="bars">
    {%- for g in languages %}
      {%- assign pct = g.size | times: 100 | divided_by: total %}
      <li><span class="bars__label">{{ g.name }}</span><span class="bars__track"><span class="bars__fill" style="width: {{ pct }}%"></span></span><span class="bars__count">{{ g.size }}</span></li>
    {%- endfor %}
    </ul>
  </section>
  <section aria-labelledby="stats-categories">
    <h3 id="stats-categories">Catégories</h3>
    <ul class="bars">
    {%- for g in categories %}
      {%- assign cat = site.data.categories | where: "id", g.name | first %}
      {%- assign pct = g.size | times: 100 | divided_by: total %}
      <li><span class="bars__label">{{ cat.emoji }} {{ cat.label }}</span><span class="bars__track"><span class="bars__fill" style="width: {{ pct }}%"></span></span><span class="bars__count">{{ g.size }}</span></li>
    {%- endfor %}
    </ul>
  </section>
</div>

## Tous les projets

{%- assign all_tags = "" | split: "" -%}
{%- for r in repos -%}{%- assign all_tags = all_tags | concat: r.tags -%}{%- endfor -%}
{%- assign all_tags = all_tags | compact | uniq | sort %}

<div class="filters" id="filters" hidden>
  <label for="filter-search" class="visually-hidden">Rechercher un projet</label>
  <input type="search" id="filter-search" placeholder="Rechercher (nom, description, langage, tag)…">
  <div class="filters__group" role="group" aria-label="Filtrer par catégorie">
    <button type="button" class="chip chip--filter is-active" data-filter-category="">Toutes</button>
    {%- for cat in site.data.categories %}
    {%- assign n = repos | where: "category", cat.id | size %}
    {%- if n > 0 %}
    <button type="button" class="chip chip--filter" data-filter-category="{{ cat.id }}">{{ cat.emoji }} {{ cat.label }} ({{ n }})</button>
    {%- endif %}
    {%- endfor %}
  </div>
  <div class="filters__group" role="group" aria-label="Filtrer par tag">
    {%- for tag in all_tags %}
    <button type="button" class="chip chip--filter chip--tag" data-filter-tag="{{ tag }}">#{{ tag }}</button>
    {%- endfor %}
  </div>
  <p class="filters__count" aria-live="polite"><span id="filter-count">{{ total }}</span> projet(s) affiché(s)</p>
</div>

<div class="repo-grid" id="repo-grid">
{%- for repo in repos %}
  {% include repo-card.html repo=repo %}
{%- endfor %}
</div>

<p class="filters__empty" id="filter-empty" hidden>Aucun projet ne correspond à ces critères.</p>

---

💡 Un dépôt à proposer ? [Remplir le formulaire de proposition]({{ site.proposal_url }}) ·
📰 [S'abonner au flux RSS]({{ '/projets/feed.xml' | relative_url }}) ·
🗓️ [Voir la chronologie]({{ '/projets/chronologie/' | relative_url }})

<script src="{{ '/assets/js/projects.js' | relative_url }}" defer></script>
