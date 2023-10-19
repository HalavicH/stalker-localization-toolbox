## Formatting of the text inside the <text> tag

Before:
```xml
<string id="ui_mm_alife_general_dyn_noct_mutants_attacks_strength_desc">
    <text>Визначає наявність нічних мутантів, тобто кількість, яка з’явиться
вночі.\n\n%c[pda_yellow]Примітка:%c[ui_gray_2]\nУстановлення на 100% призведе
до дуже небезпечних ночей. При 0 цей аддон фактично вимкнено. (За замовчуванням: 60)
    </text>
</string>
```

After:
```xml
<string id="ui_mm_alife_general_dyn_noct_mutants_attacks_strength_desc">
    <text>
        Визначає наявність нічних мутантів, тобто кількість, яка з’явиться вночі. 
      \n
      \n%c[pda_yellow]Примітка:%c[ui_gray_2]
      \nУстановлення на 100% призведе до дуже небезпечних ночей. При 0 цей аддон фактично
        вимкнено. (За замовчуванням: 60)
    </text>
</string>

```