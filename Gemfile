# Dépendances Ruby du site.
#  - groupe :jekyll_plugins : reproduit EXACTEMENT l'environnement GitHub Pages
#    (même version de Jekyll, du thème Cayman et des plugins autorisés)
#    → utilisé pour l'aperçu local : `bundle exec jekyll serve`
#  - groupe :test : outils de contrôle qualité utilisés par la CI
#    (la CI installe uniquement ce groupe : BUNDLE_WITHOUT=jekyll_plugins)
source "https://rubygems.org"

gem "github-pages", group: :jekyll_plugins

# Serveur HTTP requis par `jekyll serve` depuis Ruby 3.0
gem "webrick", "~> 1.8"

group :test do
  gem "html-proofer", "~> 5.0"
end
