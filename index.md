---
layout: default
---

<div class="profile">
  <img src="{{ '/assets/img/hicham-atatri.jpg' | relative_url }}" alt="Photo de profil de Hicham ATATRI" width="150" height="150">  
  <div class="profile-info">
    <p>📍 Rabat, Maroc | ✉️ <a href="mailto:hichamatatri@gmail.com">hichamatatri@gmail.com</a></p>
  </div>
</div>

## Professeur agrégé d’informatique en CPGE (MPSI / MP) 
- Passionné par l’algorithmique, la programmation et la pédagogie
- Propose des supports de cours, exercices, projets et ressources
- Objectif : accompagner les étudiants vers la réussite aux concours  
  
---

## Formation

- **2024 - 2025** : Agrégation en Informatique
- **2017 - 2019** : Formation au centre de préparation à l’agrégation (Marrakech)
- **2007 – 2009** : Master en Qualité Logicielle – UIT Kénitra  
- **2005 – 2006** : Centre Pédagogique Régional – Settat (Informatique)  
- **2003 – 2006** : Licence en Sciences Mathématiques et Informatique – UIT Kénitra  
- **1998 – 2001** : Baccalauréat en Sciences Mathématiques A – Kénitra  

---

## Expériences Professionnelles

- **Actuellement** : Professeur agrégé d’informatique en classes préparatoires (MPSI / MP) – Centre Molay Youssef, Rabat  
- **2019 – 2024** : Professeur en classes préparatoires aux grandes écoles d’ingénieurs   
- **2006 – 2019** : Professeur d’informatique – Rabat  
- **2015** : Formateur VBA/Excel à Hirshman Automotive Kenitra  
- **2011** : Consultant – Arig (Tierce Maintenance Applicative, tests, intégration)  
- **2011** : Vacataire – Faculté des sciences UIT Kénitra (Cours C++, encadrement Master)  

---

## Projets

{% assign featured = site.data.repositories | where: "featured", true | sort: "added" | reverse -%}
{% for repo in featured -%}
{% assign gh = "https://github.com/" | append: repo.repo -%}
{% if repo.repo %}{% assign link = repo.homepage | default: repo.url | default: gh %}{% else %}{% assign link = repo.homepage | default: repo.url %}{% endif -%}
- **[{{ repo.name }}]({{ link }})** : {{ repo.description }}
{% endfor -%}
- 👉 **[Voir tous les projets]({{ '/projets/' | relative_url }})** ({{ site.data.repositories | size }} projets, avec statistiques, filtres et [chronologie]({{ '/projets/chronologie/' | relative_url }}))
- Tous mes dépôts publics : [github.com/Hatatri](https://github.com/Hatatri)

---

## Compétences

- **Développement Web** : HTML5, PHP, Frameworks JavaScript, ... 
- **Conception & Analyse** : UML, Merise, E/A  
- **Bases de Données & Big Data** : SQL Server, MySQL, NoSQL, Hadoop, MongoDB ...  
- **Machine Learning & Data Science** :
  > Maîtrise de Python (Pandas, Scikit-learn, TensorFlow, PyTorch), SQL, R  
  > Compétences en régression, classification, clustering, NLP, réseaux de neurones  
  > Expérience en analyse exploratoire, feature engineering, évaluation de modèles  
  > Projets : prédiction de séries temporelles, analyse de sentiments, détection d’anomalies  
  > Visualisation de données (Matplotlib, Seaborn, Plotly, Power BI, Tableau)    
- **Qualité Logicielle** :  
  > **Commits clairs et fréquents**  : Utiliser des messages explicites : `Ajouter`, `Corriger`, `Améliorer`.  
  > **Organisation du projet** : Dossiers séparés : `src/`, `tests/`, `docs/`  
  > **Tests unitaires**  : pytest, testmod...  
  > **Documentation**  : Ajouter des `docstrings` aux fonctions et classes.  
  > **Style de code**  : Respecter PEP8 (Python).  
- **Gestion de Projet** :  
  > **Objectifs clairs**  : Définir les buts du projet et les livrables attendus.  
  > **Organisation des tâches**  : Créer un **Kanban GitHub Projects** (To Do / In Progress / Done).  
  > **Planification**  : Estimer l’effort (temps, complexité).  
  > **Suivi collaboratif**  : Utiliser des branches par fonctionnalité, Pull Requests pour révision avant intégration.  
  > **Documentation continue**.  
  > **Évaluation**  : Revoir la qualité du code et la progression du projet régulièrement.   

---

## Langues 

- **Arabe**    : ★★★★★  
- **Français** : ★★★★★  
- **Anglais**  : ★★★  

---

## Centres d’intérêt

- Randonnée, trekking  
- Natation  
- Football  
- Spéléologie  
- Encadrement des jeunes en centres de tourisme  

---
<!-- Bouton CV -->
<p><a class="btn-cv" href="{{ '/cv.pdf' | relative_url }}">📄 Télécharger le CV (PDF)</a></p>
