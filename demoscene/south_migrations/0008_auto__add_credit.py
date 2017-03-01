# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Credit'
        db.create_table('demoscene_credit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('production', self.gf('django.db.models.fields.related.ForeignKey')(related_name='credits', to=orm['demoscene.Production'])),
            ('nick', self.gf('django.db.models.fields.related.ForeignKey')(related_name='credits', to=orm['demoscene.Nick'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('demoscene', ['Credit'])


    def backwards(self, orm):
        
        # Deleting model 'Credit'
        db.delete_table('demoscene_credit')


    models = {
        'demoscene.credit': {
            'Meta': {'object_name': 'Credit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nick': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'credits'", 'to': "orm['demoscene.Nick']"}),
            'production': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'credits'", 'to': "orm['demoscene.Production']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'demoscene.downloadlink': {
            'Meta': {'object_name': 'DownloadLink'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'production': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'download_links'", 'to': "orm['demoscene.Production']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2048'})
        },
        'demoscene.nick': {
            'Meta': {'object_name': 'Nick'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'releaser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'nicks'", 'to': "orm['demoscene.Releaser']"})
        },
        'demoscene.nickvariant': {
            'Meta': {'object_name': 'NickVariant'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nick': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'variants'", 'to': "orm['demoscene.Nick']"})
        },
        'demoscene.platform': {
            'Meta': {'object_name': 'Platform'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'demoscene.production': {
            'Meta': {'object_name': 'Production'},
            'author_affiliation_nicks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'member_productions'", 'symmetrical': 'False', 'to': "orm['demoscene.Nick']"}),
            'author_nicks': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'productions'", 'symmetrical': 'False', 'to': "orm['demoscene.Nick']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'platforms': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'productions'", 'symmetrical': 'False', 'to': "orm['demoscene.Platform']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'types': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'productions'", 'symmetrical': 'False', 'to': "orm['demoscene.ProductionType']"})
        },
        'demoscene.productiontype': {
            'Meta': {'object_name': 'ProductionType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'demoscene.releaser': {
            'Meta': {'object_name': 'Releaser'},
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'members'", 'symmetrical': 'False', 'to': "orm['demoscene.Releaser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_group': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['demoscene']
