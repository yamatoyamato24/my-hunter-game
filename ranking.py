_memory_scores = []
def update_ranking(new_score):
    global _memory_scores
    _memory_scores.append(new_score)
    _memory_scores.sort(reverse=True)
    return _memory_scores[:5]
