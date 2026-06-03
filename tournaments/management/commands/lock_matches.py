from django.core.management.base import BaseCommand
from django.utils import timezone
from tournaments.models import Match


class Command(BaseCommand):
    help = 'Locks matches that have reached kickoff time'

    def handle(self, *args, **kwargs):
        now = timezone.now()

        matches_to_lock = Match.objects.filter(
            status=Match.Status.UPCOMING,
            kickoff_time__lte=now
        )

        count = matches_to_lock.count()

        if count == 0:
            self.stdout.write('No matches to lock.')
            return

        matches_to_lock.update(status=Match.Status.LIVE)

        self.stdout.write(
            self.style.SUCCESS(f'✅ Locked {count} match(es) — predictions closed.')
        )