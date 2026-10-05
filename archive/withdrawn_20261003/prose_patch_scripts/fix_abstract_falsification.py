with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'r') as f:
    content = f.read()

old_abstract_falsification = r"Finally, we formally falsify tabular Q-learning model classes via action-support screening."
new_abstract_falsification = r"Finally, we provide an empirical demonstration of action-support failure in tabular Q-learning model classes via action-support screening."
content = content.replace(old_abstract_falsification, new_abstract_falsification)

# Let's also check the contributions list in the intro
old_intro_falsification = r"Concurrently, we formally falsify tabular Q-learning policies via action-support screening in multi-scale environments."
new_intro_falsification = r"Concurrently, we provide an empirical demonstration of action-support failure in tabular Q-learning policies via action-support screening in multi-scale environments."
content = content.replace(old_intro_falsification, new_intro_falsification)

with open('paper/Machine_Markets_Final_Integrated_Paper.tex', 'w') as f:
    f.write(content)
print("Abstract and Intro updated.")
