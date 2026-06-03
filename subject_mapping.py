all_subjects = {
    # Active group (Subjects 1-11)
    1: {'left': 'single', 'right': 'multiple', 'group': 'active'},
    2: {'left': 'single', 'right': 'multiple', 'group': 'active'},
    3: {'left': 'multiple', 'right': 'single', 'group': 'active'},
    4: {'left': 'multiple', 'right': 'single', 'group': 'active'},
    5: {'left': 'single', 'right': 'multiple', 'group': 'active'},
    6: {'left': 'multiple', 'right': 'single', 'group': 'active'},
    7: {'left': 'multiple', 'right': 'single', 'group': 'active'},
    8: {'left': 'multiple', 'right': 'single', 'group': 'active'},
    9: {'left': 'multiple', 'right': 'single', 'group': 'active'},  # SN011 = subject 9
    10: {'left': 'single', 'right': 'multiple', 'group': 'active'},  # SN012 = subject 10
    11: {'left': 'multiple', 'right': 'single', 'group': 'active'},  # SN024 = subject 11

    # Inactive group (Subjects 12-20)
    12: {'left': 'single', 'right': 'multiple', 'group': 'inactive'},
    13: {'left': 'single', 'right': 'multiple', 'group': 'inactive'},
    14: {'left': 'multiple', 'right': 'single', 'group': 'inactive'},
    15: {'left': 'multiple', 'right': 'single', 'group': 'inactive'},
    16: {'left': 'multiple', 'right': 'single', 'group': 'inactive'},
    17: {'left': 'multiple', 'right': 'single', 'group': 'inactive'},
    18: {'left': 'single', 'right': 'multiple', 'group': 'inactive'},
    19: {'left': 'single', 'right': 'multiple', 'group': 'inactive'},
    20: {'left': 'multiple', 'right': 'single', 'group': 'inactive'},
}

print(f"Loaded {len(all_subjects)} subjects")