# Les Types de Galaxies
```
classDiagram

    note for Galaxy "Représente la classe mère de tout les types de galaxies"

  

    Galaxy <|-- HabitableGalaxy

    note for HabitableGalaxy "Représente une galaxie potentiellement habitable"

  

    Galaxy <|-- UnhabitableGalaxy

    note for UnhabitableGalaxy "Représente la version non habitable d'une Galaxie. "

  

    Galaxy <|-- GasCloud

    note for GasCloud "Représente une galaxie composé d'un regroupement concentré de gaz exotique idéale pour la recherche. "

  

    HabitableGalaxy <|-- ArtificialBody

    note for ArtificialBody "Représente une méga-structure qui agit en tant que forteresse, spatioport, ou autre."

  

    class Galaxy{

        +String name

        +String owner

  

        +int size

        +List~int position~

  

        +List~Ressource ressources~

        +List~Science sciences~

  

        +changeOwner(owner_id)

    }

  

    class HabitableGalaxy{

        +List~Building buildings~

  

        +ressource_Output()

        science_Output()

  

        +construct_Building(int building_id)

        -add_Building(int bulding_id)

    }

  

    class UnhabitableGalaxy{

        +choose_Type(Rand random)

    }

  

    class GasCloud {

        +choose_Output(Rand random)

    }

  

    class ArtificialBody {

        int artificialTypeId

    }
```
![[Galaxy UML Diagram.png]]
[Lien vers le fichier![](https://mermaid.ink/img/pako:eNqFVNtuGjEQ_ZWRX0pUyAegvjStRCu1igTt20rIsYfFktfe-NKGUPie8h38WMd7gcWg1NJ6rTmeOWfGY2-ZsBLZlAnNvf-seOl4VRigYWxAWFkHM675ywYKNsfaHQ8eDQGaQ-OCUB3_OgSJEGwMoNFD2NQ0k6VMngp9wQrTBu1iffgzmcAX_qQCf9LYGjPWDM3oozlFh5pcTFCoNVa0gHXveZv2p1m_SXyFX2f-C51X1pCPObOBfJdUzVpV93Cbfcb9J22jvKpxa34jTWGr2vrjoeEBh6WzsW4zFtYI-rsEJodXwBcb1HNEUPJ44DoVKbok3aFYo6NvKDCvdaP0owtqpYTi-sHKvEiX4A3V1fFQ8okPLooQqT-eowJeqgBoIHDSnMRRpIAOqYvG4GselK3JMgYbgcfg8P4ssZ2bluvquW1NabxfBKdMCYZXeG21vw26Pk4DKOL36nW495vyYZ_sVGNFQsz-wqOB56SUyigQXL_y-3zTQiik0wDf_v0eLgKJNTclPiZJo0bYUsm7Ft_1G9sss0PZ5kQPUWmZ8nvqFkMtF5wntcvHGOoYRndnsJM5QIZirWlPcNmTjVKJesKz9DQmXMp8X7Yty_Dqpm0vCmWtx-UPektGc24kOJpsdTvS6frciNBl9t8YWUsPIqVc-AlNir7KQQg2ZhW6iitJ72jjVrCwpptZsCktqcnRh9TJO9pJfW0XGyPYlAqLYxZryQN2Dy-brrimy8BQqmDd9-5ptmalSrb7B0i_7qM?type=png)](https://mermaid.live/edit#pako:eNqFVNtuGjEQ_ZWRX0pUyAegvjStRCu1igTt20rIsYfFktfe-NKGUPie8h38WMd7gcWg1NJ6rTmeOWfGY2-ZsBLZlAnNvf-seOl4VRigYWxAWFkHM675ywYKNsfaHQ8eDQGaQ-OCUB3_OgSJEGwMoNFD2NQ0k6VMngp9wQrTBu1iffgzmcAX_qQCf9LYGjPWDM3oozlFh5pcTFCoNVa0gHXveZv2p1m_SXyFX2f-C51X1pCPObOBfJdUzVpV93Cbfcb9J22jvKpxa34jTWGr2vrjoeEBh6WzsW4zFtYI-rsEJodXwBcb1HNEUPJ44DoVKbok3aFYo6NvKDCvdaP0owtqpYTi-sHKvEiX4A3V1fFQ8okPLooQqT-eowJeqgBoIHDSnMRRpIAOqYvG4GselK3JMgYbgcfg8P4ssZ2bluvquW1NabxfBKdMCYZXeG21vw26Pk4DKOL36nW495vyYZ_sVGNFQsz-wqOB56SUyigQXL_y-3zTQiik0wDf_v0eLgKJNTclPiZJo0bYUsm7Ft_1G9sss0PZ5kQPUWmZ8nvqFkMtF5wntcvHGOoYRndnsJM5QIZirWlPcNmTjVKJesKz9DQmXMp8X7Yty_Dqpm0vCmWtx-UPektGc24kOJpsdTvS6frciNBl9t8YWUsPIqVc-AlNir7KQQg2ZhW6iitJ72jjVrCwpptZsCktqcnRh9TJO9pJfW0XGyPYlAqLYxZryQN2Dy-brrimy8BQqmDd9-5ptmalSrb7B0i_7qM)

## Galaxie
Ar
### Habitable
Ar
### Non-Habitable
Ar
### Artificielle
Ar
## Gazeuse
Ar

# Les Types de Ressources Matérielles.
```
```

## Ressources
Ar
### Métaux - T1 et T2
Ar
#### Minerai - T1
Ar
#### Lingot - T2
Ar

 
### Métaux Précieux - T1 et T2
#### Minerai - T1
#### Lingots - T2



### Construction T1 et T2
#### Roche - T1
#### Béton - T2
### Nourriture T1


