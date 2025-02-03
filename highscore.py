def save_score(score):
    with open("high_score.txt", "w") as file:
        file.write(str(score))

def get_score():
    with open("high_score.txt", "r") as file:
        score = file.read()
    
    save_score(score)
    if score == '':
        return 0
    return int(score)
