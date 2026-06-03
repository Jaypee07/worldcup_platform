from django.core.management.base import BaseCommand
from tournaments.models import Tournament, Team, Group, Match
from predictions.models import Competition
import pytz
from datetime import datetime


class Command(BaseCommand):
    help = 'Seeds the FIFA World Cup 2026 tournament data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding tournament data...')

        tournament, _ = Tournament.objects.get_or_create(
            name='FIFA World Cup',
            year=2026,
            defaults={'is_active': True}
        )
        self.stdout.write('✓ Tournament created')

        teams_data = [
            # Group A
            ('Mexico',                  'MEX', '🇲🇽'),
            ('South Africa',            'RSA', '🇿🇦'),
            ('South Korea',             'KOR', '🇰🇷'),
            ('Czechia',                 'CZE', '🇨🇿'),

            # Group B
            ('Canada',                  'CAN', '🇨🇦'),
            ('Bosnia and Herzegovina',  'BIH', '🇧🇦'),
            ('Qatar',                   'QAT', '🇶🇦'),
            ('Switzerland',             'SUI', '🇨🇭'),

            # Group C
            ('Brazil',                  'BRA', '🇧🇷'),
            ('Morocco',                 'MAR', '🇲🇦'),
            ('Scotland',                'SCO', '🏴󠁧󠁢󠁳󠁣󠁴󠁿'),
            ('Haiti',                   'HAI', '🇭🇹'),

            # Group D
            ('USA',                     'USA', '🇺🇸'),
            ('Paraguay',                'PAR', '🇵🇾'),
            ('Australia',               'AUS', '🇦🇺'),
            ('Türkiye',                 'TUR', '🇹🇷'),

            # Group E
            ('Germany',                 'GER', '🇩🇪'),
            ('Curaçao',                 'CUW', '🇨🇼'),
            ('Ivory Coast',             'CIV', '🇨🇮'),
            ('Ecuador',                 'ECU', '🇪🇨'),

            # Group F
            ('Netherlands',             'NED', '🇳🇱'),
            ('Japan',                   'JPN', '🇯🇵'),
            ('Sweden',                  'SWE', '🇸🇪'),
            ('Tunisia',                 'TUN', '🇹🇳'),

            # Group G
            ('Iran',                    'IRN', '🇮🇷'),
            ('New Zealand',             'NZL', '🇳🇿'),
            ('Belgium',                 'BEL', '🇧🇪'),
            ('Egypt',                   'EGY', '🇪🇬'),

            # Group H
            ('Spain',                   'ESP', '🇪🇸'),
            ('Uruguay',                 'URU', '🇺🇾'),
            ('Cape Verde',              'CPV', '🇨🇻'),
            ('Saudi Arabia',            'KSA', '🇸🇦'),

            # Group I
            ('France',                  'FRA', '🇫🇷'),
            ('Senegal',                 'SEN', '🇸🇳'),
            ('Norway',                  'NOR', '🇳🇴'),
            ('Iraq',                    'IRQ', '🇮🇶'),

            # Group J
            ('Argentina',               'ARG', '🇦🇷'),
            ('Algeria',                 'ALG', '🇩🇿'),
            ('Austria',                 'AUT', '🇦🇹'),
            ('Jordan',                  'JOR', '🇯🇴'),

            # Group K
            ('Portugal',                'POR', '🇵🇹'),
            ('Uzbekistan',              'UZB', '🇺🇿'),
            ('Colombia',                'COL', '🇨🇴'),
            ('DR Congo',                'COD', '🇨🇩'),

            # Group L
            ('England',                 'ENG', '🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
            ('Croatia',                 'CRO', '🇭🇷'),
            ('Ghana',                   'GHA', '🇬🇭'),
            ('Panama',                  'PAN', '🇵🇦'),
        ]

        team_objects = {}
        for name, code, flag in teams_data:
            team, _ = Team.objects.get_or_create(
                code=code,
                defaults={'name': name, 'flag': flag}
            )
            team_objects[code] = team

        self.stdout.write(f'✓ {len(team_objects)} teams created')

        groups_data = {
            'A': ['MEX', 'RSA', 'KOR', 'CZE'],
            'B': ['CAN', 'BIH', 'QAT', 'SUI'],
            'C': ['BRA', 'MAR', 'SCO', 'HAI'],
            'D': ['USA', 'PAR', 'AUS', 'TUR'],
            'E': ['GER', 'CUW', 'CIV', 'ECU'],
            'F': ['NED', 'JPN', 'SWE', 'TUN'],
            'G': ['IRN', 'NZL', 'BEL', 'EGY'],
            'H': ['ESP', 'URU', 'CPV', 'KSA'],
            'I': ['FRA', 'SEN', 'NOR', 'IRQ'],
            'J': ['ARG', 'ALG', 'AUT', 'JOR'],
            'K': ['POR', 'UZB', 'COL', 'COD'],
            'L': ['ENG', 'CRO', 'GHA', 'PAN'],
        }

        for group_name, codes in groups_data.items():
            group, _ = Group.objects.get_or_create(
                name=group_name,
                tournament=tournament
            )
            group.teams.set([team_objects[code] for code in codes])
            group.save()

        self.stdout.write('✓ 12 groups created and assigned')

        Competition.objects.get_or_create(
            type=Competition.Type.MAIN,
            defaults={'name': 'Main Competition', 'is_active': True}
        )
        Competition.objects.get_or_create(
            type=Competition.Type.SECOND_CHANCE,
            defaults={'name': 'Second Chance', 'is_active': False}
        )
        self.stdout.write('✓ Competitions created')

        self.seed_fixtures(tournament, team_objects)

        self.stdout.write(self.style.SUCCESS('\n✅ Seeding complete.'))

    def seed_fixtures(self, tournament, team_objects):
        et = pytz.timezone('US/Eastern')

        def kt(date_str, time_str):
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            return et.localize(dt)

        fixtures = [
            # GROUP A
            ('MEX', 'RSA',  '2026-06-11', '15:00', 'A'),
            ('KOR', 'CZE',  '2026-06-11', '22:00', 'A'),
            ('CZE', 'RSA',  '2026-06-18', '12:00', 'A'),
            ('MEX', 'KOR',  '2026-06-18', '23:00', 'A'),
            ('CZE', 'MEX',  '2026-06-24', '21:00', 'A'),
            ('RSA', 'KOR',  '2026-06-24', '21:00', 'A'),

            # GROUP B
            ('CAN', 'BIH',  '2026-06-12', '15:00', 'B'),
            ('QAT', 'SUI',  '2026-06-13', '15:00', 'B'),
            ('SUI', 'BIH',  '2026-06-18', '15:00', 'B'),
            ('CAN', 'QAT',  '2026-06-18', '18:00', 'B'),
            ('SUI', 'CAN',  '2026-06-24', '15:00', 'B'),
            ('BIH', 'QAT',  '2026-06-24', '15:00', 'B'),

            # GROUP C
            ('BRA', 'MAR',  '2026-06-13', '18:00', 'C'),
            ('HAI', 'SCO',  '2026-06-13', '21:00', 'C'),
            ('SCO', 'MAR',  '2026-06-19', '18:00', 'C'),
            ('BRA', 'HAI',  '2026-06-19', '21:00', 'C'),
            ('SCO', 'BRA',  '2026-06-24', '18:00', 'C'),
            ('MAR', 'HAI',  '2026-06-24', '18:00', 'C'),

            # GROUP D
            ('USA', 'PAR',  '2026-06-12', '21:00', 'D'),
            ('AUS', 'TUR',  '2026-06-14', '00:00', 'D'),
            ('TUR', 'PAR',  '2026-06-20', '00:00', 'D'),
            ('USA', 'AUS',  '2026-06-19', '15:00', 'D'),
            ('TUR', 'USA',  '2026-06-25', '22:00', 'D'),
            ('PAR', 'AUS',  '2026-06-25', '22:00', 'D'),

            # GROUP E
            ('GER', 'CUW',  '2026-06-14', '13:00', 'E'),
            ('CIV', 'ECU',  '2026-06-14', '19:00', 'E'),
            ('GER', 'CIV',  '2026-06-20', '16:00', 'E'),
            ('ECU', 'CUW',  '2026-06-20', '20:00', 'E'),
            ('ECU', 'GER',  '2026-06-25', '16:00', 'E'),
            ('CUW', 'CIV',  '2026-06-25', '16:00', 'E'),

            # GROUP F
            ('NED', 'JPN',  '2026-06-14', '16:00', 'F'),
            ('SWE', 'TUN',  '2026-06-14', '22:00', 'F'),
            ('NED', 'SWE',  '2026-06-20', '13:00', 'F'),
            ('TUN', 'JPN',  '2026-06-21', '00:00', 'F'),
            ('JPN', 'SWE',  '2026-06-25', '19:00', 'F'),
            ('TUN', 'NED',  '2026-06-25', '19:00', 'F'),

            # GROUP G
            ('BEL', 'EGY',  '2026-06-15', '18:00', 'G'),
            ('IRN', 'NZL',  '2026-06-16', '00:00', 'G'),
            ('BEL', 'IRN',  '2026-06-21', '15:00', 'G'),
            ('NZL', 'EGY',  '2026-06-21', '21:00', 'G'),
            ('EGY', 'IRN',  '2026-06-26', '23:00', 'G'),
            ('NZL', 'BEL',  '2026-06-26', '23:00', 'G'),

            # GROUP H
            ('ESP', 'CPV',  '2026-06-15', '13:00', 'H'),
            ('KSA', 'URU',  '2026-06-15', '18:00', 'H'),
            ('ESP', 'KSA',  '2026-06-21', '12:00', 'H'),
            ('URU', 'CPV',  '2026-06-21', '18:00', 'H'),
            ('CPV', 'KSA',  '2026-06-26', '20:00', 'H'),
            ('URU', 'ESP',  '2026-06-26', '20:00', 'H'),

            # GROUP I
            ('FRA', 'SEN',  '2026-06-16', '15:00', 'I'),
            ('IRQ', 'NOR',  '2026-06-16', '18:00', 'I'),
            ('FRA', 'IRQ',  '2026-06-22', '17:00', 'I'),
            ('NOR', 'SEN',  '2026-06-22', '20:00', 'I'),
            ('NOR', 'FRA',  '2026-06-26', '15:00', 'I'),
            ('SEN', 'IRQ',  '2026-06-26', '15:00', 'I'),

            # GROUP J
            ('ARG', 'ALG',  '2026-06-16', '21:00', 'J'),
            ('AUT', 'JOR',  '2026-06-17', '00:00', 'J'),
            ('ARG', 'AUT',  '2026-06-22', '13:00', 'J'),
            ('JOR', 'ALG',  '2026-06-22', '23:00', 'J'),
            ('ALG', 'AUT',  '2026-06-27', '22:00', 'J'),
            ('JOR', 'ARG',  '2026-06-27', '22:00', 'J'),

            # GROUP K
            ('POR', 'COD',  '2026-06-17', '13:00', 'K'),
            ('UZB', 'COL',  '2026-06-17', '22:00', 'K'),
            ('POR', 'UZB',  '2026-06-23', '13:00', 'K'),
            ('COL', 'COD',  '2026-06-23', '22:00', 'K'),
            ('COL', 'POR',  '2026-06-27', '19:30', 'K'),
            ('COD', 'UZB',  '2026-06-27', '19:30', 'K'),

            # GROUP L
            ('ENG', 'CRO',  '2026-06-17', '16:00', 'L'),
            ('GHA', 'PAN',  '2026-06-17', '19:00', 'L'),
            ('ENG', 'GHA',  '2026-06-23', '16:00', 'L'),
            ('PAN', 'CRO',  '2026-06-23', '19:00', 'L'),
            ('PAN', 'ENG',  '2026-06-27', '17:00', 'L'),
            ('CRO', 'GHA',  '2026-06-27', '17:00', 'L'),
        ]

        created = 0
        skipped = 0
        for home_code, away_code, date, time, group_name in fixtures:
            home = team_objects.get(home_code)
            away = team_objects.get(away_code)

            if not home or not away:
                self.stdout.write(
                    f'  ⚠ Skipping {home_code} vs {away_code} — team not found'
                )
                skipped += 1
                continue

            group = Group.objects.get(name=group_name, tournament=tournament)

            _, made = Match.objects.get_or_create(
                tournament=tournament,
                home_team=home,
                away_team=away,
                group=group,
                defaults={
                    'stage': Match.Stage.GROUP,
                    'status': Match.Status.UPCOMING,
                    'kickoff_time': self.kt(date, time),
                }
            )
            if made:
                created += 1

        self.stdout.write(f'✓ {created} fixtures created, {skipped} skipped')

    def kt(self, date_str, time_str):
        et = pytz.timezone('US/Eastern')
        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return et.localize(dt)