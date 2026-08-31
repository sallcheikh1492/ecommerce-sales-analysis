# Rapport d'Analyse — E-commerce Sales Analysis

**Date :** Mai 2026  
**Auteur :** Data Analyst  
**Dataset :** UCI E-commerce Data (Dec 2010 – Dec 2011)

---

## 1. Résumé Exécutif

Ce rapport présente une analyse complète des ventes d'un e-commerce britannique spécialisé
dans les cadeaux et objets de décoration. L'analyse couvre 12 mois de transactions et
s'appuie sur des techniques SQL, Python et une segmentation RFM.

---

## 2. KPIs Principaux

| Indicateur | Valeur estimée |
|---|---|
| Chiffre d'affaires total | £8 911 407.90 |
| Nombre de commandes | 18 532 |
| Nombre de clients actifs | 4 338 |
| Panier moyen | £480.87 |
| Produits référencés | 3 665 |
| Taux de réachat | ~70 % |

---

## 3. Insights Produits

### 3.1 Produits les plus rentables
- Les articles de décoration saisonnière (Noël, Pâques) dominent les ventes en volume.
- Les articles à prix unitaire élevé (>£5) génèrent 60 % du CA malgré 30 % des volumes.
- **Recommandation :** Augmenter les stocks des top produits avant novembre (période de pic).

### 3.2 Saisonnalité
- **Pic de novembre** : CA 3× supérieur à la moyenne mensuelle (achats anticipés Noël).
- **Creux de janvier-février** : période de soldes post-fêtes.
- **Recommandation :** Lancer des campagnes promotionnelles en janvier pour soutenir le CA.

---

## 4. Insights Clients

### 4.1 Concentration du CA
- Le top 10 % des clients génère ~55 % du chiffre d'affaires (loi de Pareto appliquée).
- Le marché UK représente ~85 % des ventes, suivi par l'Allemagne, la France, et les Pays-Bas.

### 4.2 Segmentation RFM

| Segment | % Clients | % CA | Action prioritaire |
|---|---|---|---|
| **Champions** | ~15 % | ~45 % | Programme VIP, fidélisation |
| **Clients fidèles** | ~20 % | ~25 % | Cross-sell, up-sell |
| **Clients potentiels** | ~20 % | ~15 % | Ré-engagement, promo ciblée |
| **Clients à risque** | ~25 % | ~10 % | Win-back campaign |
| **Clients perdus** | ~20 % | ~5 % | Dernière chance, puis abandon |

---

## 5. Insights Géographiques

- **United Kingdom** : marché dominant, panier moyen modéré.
- **Netherlands & EIRE** : panier moyen élevé, fort potentiel de croissance.
- **Allemagne & France** : volume croissant, opportunité de localisation (site FR/DE).
- **Recommandation :** Investir en SEO/SEA sur les marchés européens à fort panier moyen.

---

## 6. Recommandations Stratégiques

### Court terme (0-3 mois)
1. **Relancer les Clients à risque** via email win-back avec réduction de 20 %.
2. **Créer un programme de fidélité** pour les Champions (accès VIP, avant-premières).
3. **Optimiser les stocks** pour les 10 produits stars avant la période de fêtes.

### Moyen terme (3-6 mois)
4. **Développer le cross-sell** : recommander des produits complémentaires aux Clients fidèles.
5. **Localiser le site** en allemand et français pour capturer les marchés européens.
6. **Automatiser les emails** selon le segment RFM (Klaviyo, Mailchimp, Brevo).

### Long terme (6-12 mois)
7. **Implémenter un moteur de recommandation** basé sur le comportement d'achat.
8. **Prédire le churn** avec un modèle ML (Random Forest / Gradient Boosting).
9. **Tester des campagnes A/B** sur les offres promotionnelles par segment.

---

## 7. Conclusion

L'analyse révèle un e-commerce en bonne santé avec une clientèle fidèle et une forte
concentration sur le marché UK. Les principaux leviers de croissance sont :
- La **rétention des Champions** (impact CA immédiat)
- La **réactivation des Clients à risque** (récupération de CA perdu)
- L'**expansion européenne** (marchés à fort panier moyen)

La combinaison SQL + Python + Power BI permet un suivi en temps quasi-réel de ces KPIs
et facilitera la prise de décision data-driven.

---

*Rapport généré dans le cadre du projet BI « E-commerce Sales Analysis »*
