from django.db import migrations


def create_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.create(
        id=1,
        domain='127.0.0.1:8000',
        name='localhost'
    )


def reverse_default_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.filter(id=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('recipes', '0002_comment_rating'),
    ]

    operations = [
        migrations.RunPython(create_default_site, reverse_default_site),
    ]