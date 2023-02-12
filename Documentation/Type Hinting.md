Le type hinting en Python est une fonctionnalité qui permet de définir le type d'une variable, d'une fonction ou d'un objet. Il sert à fournir une documentation supplémentaire pour les développeurs, ainsi qu'à améliorer la qualité du code en permettant de détecter des erreurs de type plus tôt dans le processus de développement.

Voici un exemple de comment utiliser le type hinting pour définir le type d'une variable :
```python
x: int = 10
```

Dans cet exemple, nous définissons une variable `x` de type `int`. Cela signifie que la variable `x` ne peut être assignée qu'à une valeur de type `int`. Si nous essayons de l'assigner à une valeur de type différent, nous obtiendrons une erreur.

Voici un exemple de comment utiliser le type hinting pour définir le type d'une fonction :
```python
def add(a: int, b: int) -> int:
    return a + b
```
Dans cet exemple, nous définissons une fonction `add` qui prend en entrée deux variables `a` et `b` de type `int`, et qui retourne une valeur de type `int`. Cela signifie que la fonction `add` ne peut être appelée avec des arguments de type différent, et que le résultat sera toujours de type `int`.

Le type hinting peut également être utilisé pour définir le type d'un objet en utilisant des annotations de classe :
```python
class Point:
    x: float
    y: float
```
Dans cet exemple, nous définissons une classe `Point` avec deux attributs `x` et `y` de type `float`. Cela signifie que les attributs `x` et `y` ne peuvent être assignés qu'à des valeurs de type `float`.

En conclusion, le type hinting en Python est un outil utile pour améliorer la qualité du code en permettant de détecter des erreurs de type plus tôt dans le processus de développement, et en fournissant une documentation supplémentaire pour les développeurs. Il est facile à utiliser et peut être ajouté à n'importe quelle partie de votre code, y compris les variables, les fonctions et les classes.