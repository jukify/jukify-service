import argparse

from jukifyservice.models import UsageData, Group

def generate_usage_input(output_file='input_data.tsv'):
    rows = [[d.user_id, d.track_id, str(d.rating)] for d in UsageData.objects.all()]
    with open(output_file, 'w') as file:
        file.writelines('\t'.join(i) + '\n' for i in rows)

def generate_groups_input(output_file='groups.tsv'):
    rows = [[g.id, g.users.all()] for g in Group.objects.all()]
    valid_rows = [x for x in rows if bool(x[1]) == True]
    with open(output_file, 'w') as file:
        for group in valid_rows:
            for user in group[1]:
                file.write("%s\t%s\n" % (group[0], user.id))

