# Les dictionnaires en python.
## Introduction
Un dictionnaire en Python est une collection **non ordonnée** de paires **clé-valeur**. Les clés sont **uniques et** peuvent être de n'importe quel type **immuable** (par exemple, des chaînes, des nombres entiers, etc.), tandis que les **valeurs peuvent être de n'importe quel type**. Les dictionnaires sont définis en utilisant des accolades **`{}`**.
## Exemple
```python
ressources = {
    'énergie': 100,
    'métal': 500,
    'roche': 250
}
```
## Accéder à une valeur

Pour accéder à la valeur associée à une clé donnée, vous pouvez utiliser l'opérateur de indexation `[]`. Par exemple, pour accéder à la quantité de métal dans le dictionnaire `ressources`, vous pouvez faire :

```python
metal = ressources['métal'] print(Metal ) # 500
```

## Ajouter une entrée

Vous pouvez ajouter une entrée à un dictionnaire en utilisant l'opérateur d'indexation `[]`. Par exemple, pour ajouter une entrée pour le cuivre à notre dictionnaire `ressources`, vous pouvez faire :

```python
ressources['cuivre'] = 750
```

## Modifier une entrée

Vous pouvez également modifier une entrée en utilisant l'opérateur d'indexation `[]`. Par exemple, pour augmenter la quantité de métal dans notre dictionnaire `ressources` de 100 unités, vous pouvez faire :

```python
ressources['métal'] += 100
```

## Supprimer une entrée

Vous pouvez utiliser la commande `del` pour supprimer une entrée d'un dictionnaire. Par exemple, pour supprimer l'entrée pour le cuivre de notre dictionnaire `ressources`, vous pouvez faire :

```python

del ressources['cuivre']
```

## Boucles et opérations sur les dictionnaires

Vous pouvez utiliser une boucle `for` pour parcourir les entrées d'un dictionnaire. Par exemple, pour afficher les clés et les valeurs de notre dictionnaire `ressources`, vous pouvez faire :

```python
for key, value in ressources.items():     
	print(key, value)
```

Vous pouvez également utiliser les fonctions `len()` pour obtenir la longueur d'un dictionnaire (c'est-à-dire le nombre d'entrées) et `sorted()` pour trier les clés d'un dictionnaire. Par exemple :

```python
print(len(ressources)) # 3 print
```