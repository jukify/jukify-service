from jukifyservice.models import UsageData

def generate_input():
    output_file = 'input_data.tsv'
    rows = [[d.user_id, d.track_id, str(d.rating)] for d in UsageData.objects.all()]
    with open(output_file, 'w') as file:
        file.writelines('\t'.join(i) + '\n' for i in rows)
