# cmtools
Collection of scripts and tools for ***filesystem modding*** of Crazy Machines, a 2003 puzzle/sandbox game by FAKT Software.
### Q: What do you mean by filesystem mods?
A: Filesystem mods are all modifications that don't involve binary patches or code injection. They can be copied into a vanilla copy but can't be created without these tools. While the actual game logic is compiled into the executable, there are files like `elements.fsc` and `.vsc` files that define some visuals and properties.
### Q: What can these mods do?
A: Filesystem mods are quite limited. Have some examples to get an estimate of modding limits:
#### It's possible to...
- Remove limits for element count (and open Professor's Lab in editor mode!)
- Change .ucm models, their hitboxes and tag (connector) positions
- Add rotation/flipping functionality to more elements. This can lead to interesting results with multi-model elements...
- Rearrange some of UI layout
- Add custom physic elements, albeit with properties of existing ones. Mass scales!
- Add more gears or wheels with different gear ratios or wheel radius: this stuff is defined in `elements.fsc`
#### ...but not possible to
- Make elements flammable or magnetic
- Control strength of effectors (heat, wind, light and others)
- Change most element properties like burning time, joint stiffness, etc
- Implement custom logic for elements. That's hardcoded

Details will be explained in the project wiki.

---
Сборник скриптов и инструментов для "файлового моддинга" для старой доброй Заработало! (Мастерская изобретателя, Новые испытания, Повелитель механизмов, Играет вся семья)
### Q: Что за моды?
A: Файловые моды — все те, что не используют патчи экзешника игры или инъекции кода. Их можно скопировать на ванильную копию игры, но создавать их придётся вот этими скриптами. Несмотря на то, что сама логика игры вкомпилена в бинарь, есть файлы `elements.fsc` и разные `.vsc`, в которых определяются более высокоуровневые вещи.
### Q: Что они могут?
A: Возможности весьма ограничены. Вот некоторые примеры:
#### Можно...
- Снять то самое ограничение на число элементов в "Моих экспериментах" (и открыть лабораторию Профессора на редактирование!)
- Изменять модельки .ucm с их хитбоксами и тегами (точками присоединения проводов, верёвок, ремней и т.д.)
- Добавить возможность поворота или флипа тем элементам, которые поворачивать вообще-то нельзя. На сложных элементах работает крайне странно, поэтому скучно точно не будет 
- Играться с раскладкой интерфейса
- Добавлять свои физические элементы, но со свойствами существующих. Но масса зависит от размера!
- Добавлять больше колёс и шестерёнок с другими передаточными числами и радиусами ремней — эти свойства вынесены в `elements.fsc`
#### ...но невозможно
- Заставить элементы гореть или магнититься
- Управлять мощностью огня, ветра, света и других эффекторов
- Менять большинство свойств элементов: время горения, жёсткость шарниров и т.д.
- Реализовать свою логику работы элементов. Это зашито в код

Подробности будут описаны на гитхабной wiki.
