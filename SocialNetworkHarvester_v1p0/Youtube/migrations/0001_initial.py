# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2018-07-12 16:12
from __future__ import unicode_literals

import SocialNetworkHarvester_v1p0.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('SocialNetworkHarvester_v1p0', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_time', models.DateTimeField(default=SocialNetworkHarvester_v1p0.models.djangoNow)),
                ('value', models.BigIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContentImage',
            fields=[
                ('image_time_label_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='SocialNetworkHarvester_v1p0.Image_time_label')),
            ],
            options={
                'abstract': False,
            },
            bases=('SocialNetworkHarvester_v1p0.image_time_label',),
        ),
        migrations.CreateModel(
            name='DislikeCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_time', models.DateTimeField(default=SocialNetworkHarvester_v1p0.models.djangoNow)),
                ('value', models.BigIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FavoriteCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_time', models.DateTimeField(default=SocialNetworkHarvester_v1p0.models.djangoNow)),
                ('value', models.BigIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LikeCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_time', models.DateTimeField(default=SocialNetworkHarvester_v1p0.models.djangoNow)),
                ('value', models.BigIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubscriberCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_time', models.DateTimeField(default=SocialNetworkHarvester_v1p0.models.djangoNow)),
                ('value', models.BigIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_time', models.DateTimeField(default=SocialNetworkHarvester_v1p0.models.djangoNow)),
                ('ended', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VideoCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_time', models.DateTimeField(default=SocialNetworkHarvester_v1p0.models.djangoNow)),
                ('value', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ViewCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_time', models.DateTimeField(default=SocialNetworkHarvester_v1p0.models.djangoNow)),
                ('value', models.BigIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='YTChannel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_ident', models.CharField(max_length=128, null=True, unique=True)),
                ('userName', models.CharField(max_length=32, null=True)),
                ('description', models.CharField(max_length=8192, null=True)),
                ('keywords', models.CharField(max_length=1000, null=True)),
                ('profileColor', models.CharField(max_length=16, null=True)),
                ('title', models.CharField(max_length=512, null=True)),
                ('publishedAt', models.DateTimeField(null=True)),
                ('hiddenSubscriberCount', models.BooleanField(default=False)),
                ('isLinked', models.BooleanField(default=False)),
                ('privacyStatus', models.CharField(max_length=32, null=True)),
                ('commentCount', models.BigIntegerField(null=True)),
                ('subscriberCount', models.BigIntegerField(null=True)),
                ('videoCount', models.IntegerField(null=True)),
                ('viewCount', models.BigIntegerField(null=True)),
                ('_last_updated', models.DateTimeField(null=True)),
                ('_last_video_harvested', models.DateTimeField(null=True)),
                ('_error_on_update', models.BooleanField(default=False)),
                ('_error_on_harvest', models.BooleanField(default=False)),
                ('_update_frequency', models.IntegerField(default=1)),
                ('_harvest_frequency', models.IntegerField(default=1)),
                ('_has_reached_begining', models.BooleanField(default=False)),
                ('_error_on_comment_harvest', models.BooleanField(default=False)),
                ('_last_comment_harvested', models.DateTimeField(null=True)),
                ('_earliest_comment_page_token', models.CharField(max_length=512, null=True)),
                ('_has_reached_comments_begining', models.BooleanField(default=False)),
                ('_last_subs_harvested', models.DateTimeField(null=True)),
                ('_public_subscriptions', models.BooleanField(default=True)),
                ('_last_playlists_harvested', models.DateTimeField(null=True)),
                ('_deleted_at', models.DateTimeField(null=True)),
                ('featuredChannel', models.ManyToManyField(related_name='_ytchannel_featuredChannel_+', to='Youtube.YTChannel')),
            ],
        ),
        migrations.CreateModel(
            name='YTComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_ident', models.CharField(max_length=128, unique=True)),
                ('text', models.CharField(max_length=8192, null=True)),
                ('text_truncated', models.BooleanField(default=False)),
                ('publishedAt', models.DateTimeField(null=True)),
                ('updatedAt', models.DateTimeField(null=True)),
                ('likeCount', models.BigIntegerField(default=0)),
                ('numberOfReplies', models.IntegerField(default=0)),
                ('_deleted_at', models.DateTimeField(null=True)),
                ('_last_updated', models.DateTimeField(null=True)),
                ('_error_on_update', models.BooleanField(default=False)),
                ('_update_frequency', models.IntegerField(default=2)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='posted_comments', to='Youtube.YTChannel')),
                ('channel_target', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='Youtube.YTChannel')),
                ('parent_comment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='Youtube.YTComment')),
            ],
        ),
        migrations.CreateModel(
            name='YTPlaylist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_ident', models.CharField(max_length=64, unique=True)),
                ('title', models.CharField(max_length=256, null=True)),
                ('description', models.CharField(max_length=4096, null=True)),
                ('publishedAt', models.DateTimeField(null=True)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('privacy_status', models.CharField(max_length=32, null=True)),
                ('video_count', models.IntegerField(null=True)),
                ('_last_updated', models.DateTimeField(null=True)),
                ('_error_on_update', models.BooleanField(default=False)),
                ('_last_video_harvested', models.DateTimeField(null=True)),
                ('_error_on_harvest', models.BooleanField(default=False)),
                ('channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='playlists', to='Youtube.YTChannel')),
            ],
        ),
        migrations.CreateModel(
            name='YTPlaylistItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playlistOrder', models.IntegerField(null=True)),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='Youtube.YTPlaylist')),
            ],
        ),
        migrations.CreateModel(
            name='YTVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_ident', models.CharField(max_length=128, unique=True)),
                ('publishedAt', models.DateTimeField(null=True)),
                ('title', models.CharField(max_length=128, null=True)),
                ('description', models.CharField(max_length=8192, null=True)),
                ('contentRating_raw', models.CharField(max_length=2048, null=True)),
                ('privacyStatus', models.CharField(max_length=32, null=True)),
                ('publicStatsViewable', models.BooleanField(default=True)),
                ('recordingLocation', models.CharField(max_length=256, null=True)),
                ('streamStartTime', models.DateTimeField(null=True)),
                ('streamEndTime', models.DateTimeField(null=True)),
                ('streamConcurrentViewers', models.IntegerField(null=True)),
                ('view_count', models.IntegerField(null=True)),
                ('like_count', models.IntegerField(null=True)),
                ('dislike_count', models.IntegerField(null=True)),
                ('favorite_count', models.IntegerField(null=True)),
                ('comment_count', models.IntegerField(null=True)),
                ('_deleted_at', models.DateTimeField(null=True)),
                ('_last_updated', models.DateTimeField(null=True)),
                ('_error_on_update', models.BooleanField(default=False)),
                ('_update_frequency', models.IntegerField(default=1)),
                ('_file_path', models.CharField(max_length=512, null=True)),
                ('channel', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='Youtube.YTChannel')),
            ],
        ),
        migrations.AddField(
            model_name='ytplaylistitem',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='playlistsSpots', to='Youtube.YTVideo'),
        ),
        migrations.AddField(
            model_name='ytcomment',
            name='video_target',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='Youtube.YTVideo'),
        ),
        migrations.AddField(
            model_name='viewcount',
            name='channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='view_counts', to='Youtube.YTChannel'),
        ),
        migrations.AddField(
            model_name='viewcount',
            name='video',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='view_counts', to='Youtube.YTVideo'),
        ),
        migrations.AddField(
            model_name='videocount',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='video_counts', to='Youtube.YTChannel'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='Youtube.YTChannel'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='value',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to='Youtube.YTChannel'),
        ),
        migrations.AddField(
            model_name='subscribercount',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriber_counts', to='Youtube.YTChannel'),
        ),
        migrations.AddField(
            model_name='likecount',
            name='comment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='like_counts', to='Youtube.YTComment'),
        ),
        migrations.AddField(
            model_name='likecount',
            name='video',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='like_counts', to='Youtube.YTVideo'),
        ),
        migrations.AddField(
            model_name='favoritecount',
            name='video',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favorite_counts', to='Youtube.YTVideo'),
        ),
        migrations.AddField(
            model_name='dislikecount',
            name='video',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dislike_counts', to='Youtube.YTVideo'),
        ),
        migrations.AddField(
            model_name='contentimage',
            name='channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='Youtube.YTChannel'),
        ),
        migrations.AddField(
            model_name='contentimage',
            name='video',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='Youtube.YTVideo'),
        ),
        migrations.AddField(
            model_name='commentcount',
            name='channel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_counts', to='Youtube.YTChannel'),
        ),
        migrations.AddField(
            model_name='commentcount',
            name='video',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment_counts', to='Youtube.YTVideo'),
        ),
    ]
