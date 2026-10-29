from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('onlinecourse', '0001_initial')]
    operations = [
        migrations.AlterField('question', 'content', models.CharField(max_length=200, db_column='content')),
        migrations.RenameField('question', 'content', 'question_text'),
        migrations.AlterField('choice', 'content', models.CharField(max_length=200, db_column='content')),
        migrations.RenameField('choice', 'content', 'choice_text'),
        migrations.AlterField('question', 'grade', models.IntegerField(default=50)),
    ]
