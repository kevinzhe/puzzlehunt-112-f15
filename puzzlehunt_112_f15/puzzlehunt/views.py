from django.shortcuts import render
from django.http import HttpResponse #tmp
from django.contrib.auth.decorators import login_required
from .models import *


def home(request):
    return render(request, 'puzzlehunt/home.html')

@login_required
def puzzle(request, puzzle_id):
    # Get the team
    try: team = TeamMember.objects.get(user=request.user).team
    except TeamMember.DoesNotExist: return redirect(home)
    # Get the puzzle+hints
    puzzle = get_object_or_404(Puzzle, pk=puzzle_id)
    hints = Hint.objects.filter(puzzle=puzzle)
    # Get the progress
    try: progress = PuzzleProgress.objects.get(puzzle=puzzle, team=team)
    except PuzzleProgress.DoesNotExist:
        progress = PuzzleProgress(
            team        = team,
            puzzle      = puzzle,
            start_time  = now()
        )
        progress.save()
    for hint in hints:
        hint.can_show = progress.start_time+hint.time_shown < now()
        hint.time_to_show = int((progress.start_time+hint.time_shown).timestamp())
    # Render the view
    template_info = {
        'order':        puzzle.order,
        'title':        puzzle.title,
        'subtitle':     puzzle.subtitle,
        'flavortext':   puzzle.flavortext,
        'par_score':    puzzle.par_score,
        'start_time':   progress.start_time,
        'end_time':     progress.end_time,
        'completed_in': progress.completed_in, 
        'score':        progress.score,
        'par_duration_human': puzzle.time_limit,
        'par_duration': int(puzzle.time_limit.total_seconds()),
        'hints':        hints,
    }
    return render(request, 'puzzlehunt/puzzle.html', template_info)

@login_required
def puzzle_index(request):
    return render(request, 'puzzlehunt/puzzle-index.html', {'puzzles':Puzzle.objects.all()})
