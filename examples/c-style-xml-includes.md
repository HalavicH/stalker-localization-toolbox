## Resolve XML C-style includes

## Before
### In file1.xml
```xml
<?xml version="1.0" encoding="windows-1251" standalone="yes" ?>
<string_table>
    #include "text\ukr\file1_includes.xml"
</string_table>
```
### In file1_includes.xml
```xml
<string id="ui_mcm_21_game_value_card_21_max_rate">
    <text>Встановити максимальну ставку</text>
</string>
<string id="st_unique_treasure_spot_descr">
    <text>Схованка. Код доступу</text>
</string>
<string id="st_question_game_reward_advice">
    <text>Зароблена порада:</text>
</string>
<string id="st_question_game_reward_money">
    <text>Отримано додаткові гроші:</text>
</string>
```

## After:
### In file1.xml
```xml
<?xml version="1.0" encoding="windows-1251" standalone="yes" ?>
<string_table>
    <!-- In file1_includes.xml -->
    <string id="ui_mcm_21_game_value_card_21_max_rate">
        <text>Встановити максимальну ставку</text>
    </string>
    <string id="st_unique_treasure_spot_descr">
        <text>Схованка. Код доступу</text>
    </string>
    <string id="st_question_game_reward_advice">
        <text>Зароблена порада:</text>
    </string>
    <string id="st_question_game_reward_money">
        <text>Отримано додаткові гроші:</text>
    </string>
</string_table>
```
No `file1_includes.xml`