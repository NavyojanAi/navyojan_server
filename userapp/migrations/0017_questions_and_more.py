# Generated by Django 5.0.7 on 2024-11-26 17:37

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('userapp', '0016_verification_delete_emailverification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_modified', models.DateTimeField(auto_now=True, null=True)),
                ('datetime_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('text', models.TextField()),
                ('category', models.CharField(choices=[('financial_personal', ' Financial and Personal'), ('ambition_problems_challenges', 'Ambitions, Problems, and Challenges'), ('scholarship_details', 'Scholarship Details'), ('agreement', 'Agreement')], max_length=50)),
                ('options', models.JSONField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='userprofilescholarshipprovider',
            name='org_site',
        ),
        migrations.RemoveField(
            model_name='userprofilescholarshipprovider',
            name='organisation',
        ),
        migrations.AddField(
            model_name='baseuserprofile',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='baseuserprofile',
            name='city',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='baseuserprofile',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='baseuserprofile',
            name='pin_code',
            field=models.CharField(blank=True, max_length=6, validators=[django.core.validators.RegexValidator('^\\d{6}$')]),
        ),
        migrations.AddField(
            model_name='baseuserprofile',
            name='state',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='annual_household_income',
            field=models.CharField(blank=True, choices=[('less_than_1_lakh', 'Less than ₹1,00,000'), ('1_to_3_lakhs', '₹1,00,001 - ₹3,00,000'), ('3_to_5_lakhs', '₹3,00,001 - ₹5,00,000'), ('5_to_10_lakhs', '₹5,00,001 - ₹10,00,000'), ('more_than_10_lakhs', 'More than ₹10,00,000')], max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='are_siblings_pursuing_education',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='current_academic_year',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='fathers_occupation',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='has_siblings',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_receiving_scholarships',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mothers_occupation',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='number_of_siblings',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='parent_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='school_college_university',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='userprofilescholarshipprovider',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='userprofilescholarshipprovider',
            name='contact_person_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='userprofilescholarshipprovider',
            name='contact_phone_number',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='userprofilescholarshipprovider',
            name='provider_type',
            field=models.CharField(choices=[('organization', 'Organization'), ('individual', 'Individual')], default='organization', max_length=15),
        ),
        migrations.AddField(
            model_name='userprofilescholarshipprovider',
            name='website',
            field=models.URLField(blank=True, validators=[django.core.validators.URLValidator()]),
        ),
        migrations.AlterField(
            model_name='baseuserprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=10, null=True, validators=[django.core.validators.RegexValidator('^\\d{10}$')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='education_level',
            field=models.CharField(blank=True, choices=[('standard_1_5', 'Standard 1–5'), ('standard_6_10', 'Standard 6–10'), ('higher_secondary', 'Higher Secondary'), ('undergraduate', 'Undergraduate'), ('postgraduate', 'Postgraduate'), ('phd', 'PhD')], max_length=20),
        ),
        migrations.CreateModel(
            name='QuestionResponses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_modified', models.DateTimeField(auto_now=True, null=True)),
                ('datetime_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('answer', models.TextField()),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(limit_choices_to={'model__in': ['scholarshipdata', 'user']}, on_delete=django.db.models.deletion.CASCADE, related_name='add_ons', to='contenttypes.contenttype')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='userapp.questions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
