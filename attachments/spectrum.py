from sqlalchemy import (Column, Integer, MetaData, String, Table, Text, Boolean, create_engine, ARRAY, DateTime, ForeignKey, JSON, desc, BigInteger, Float, asc)
from databases import Database
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi import HTTPException, Header, Depends, Query, Response, Cookie
import sys, os, json, socket, string, logging, secrets
from os import path
from enum import Enum
from datetime import datetime, timedelta, date
import serial


DATABASE_URL = 'postgresql://postgres:barc123@localhost/spectrum'


engine = create_engine(DATABASE_URL)
metadata = MetaData()

# ENERGY CALIBRATION   >>

db.define_table = Table('tbl_EnergyCalibrations',metadata,
                Column('name', 'string', notnull=True),
                Column('axx', 'double', notnull=True),
                Column('bx', 'double', notnull=True),
                Column('constant', 'double', notnull=True),
                Column('deviceName', 'string', notnull=True),

                Column('HV', 'integer', notnull=True),
                Column('Gain', 'integer', notnull=True),
                Column('LLD', 'integer', notnull=True),
                Column('duration', 'integer', notnull=True),
                Column('geometry', 'reference tbl_Geometry', notnull=True),
                Column('clientIP', 'string', notnull=True),
                Column('uniqueId', 'string', notnull=True, default='123e4567-e89b-12d3-a456-426655440000'),
                Column('is_active', 'boolean', notnull=True, default=False),
                Column('created_on', 'datetime', notnull=True, default=request.now),
                Column('created_by', 'reference auth_user', notnull=True, ondelete='CASCADE'))
db.tbl_EnergyCalibrations._after_insert.append(lambda f, id: db(db.tbl_CacheStatus.name == 'tbl_EnergyCalibrations').update(lastUpdatedOn = request.now))
db.tbl_EnergyCalibrations._after_update.append(lambda s, f:  db(db.tbl_CacheStatus.name == 'tbl_EnergyCalibrations').update(lastUpdatedOn = request.now))


# EFFICIENY CLAIBRATION FACTORS >>

db.define_table = Table('tbl_EffFactors',metadata,
                Column('nuclide', 'reference tbl_Radionuclides', notnull=True),
                Column('geometry', 'reference tbl_Geometry', notnull=True),
                Column('deviceName', 'string', notnull=True),
                Column('effFactor', 'double', notnull=True),
                Column('dataSetId', 'reference tbl_DataSet', notnull=True),
                Column('clientIP', 'string', notnull=True, readable=False, writable=False),
                Column('created_on', 'datetime', notnull=True),
                Column('created_by', 'reference auth_user', notnull=True, ondelete='CASCADE'))
db.tbl_EffFactors._after_insert.append(lambda f, id: db(db.tbl_CacheStatus.name == 'tbl_EffFactors').update(lastUpdatedOn = request.now))
db.tbl_EffFactors._after_update.append(lambda s, f:  db(db.tbl_CacheStatus.name == 'tbl_EffFactors').update(lastUpdatedOn = request.now))


# ROI >>

db.define_table = Table('tbl_ROI',metadata,
                Column('fromChannel', integer, notnull=True),
                Column('toChannel', integer, notnull=True),
                Column('colorCode', String, notnull=True),
                Column('mclass', 'reference tbl_Classes', notnull=True),
                Column('nuclide', 'reference tbl_Radionuclides', notnull=True),
                Column('geometry', 'reference tbl_Geometry', notnull=True),
                Column('created_on', datetime, notnull=True),
                Column('is_active', boolean, notnull=True, default=True),
                Column('created_by', 'reference auth_user', notnull=True, ondelete='CASCADE'))


# DOSE CLACULATION >>
db.define_table = Table('tbl_DoseCalculations',metadata,
                Column('name', string, requires=IS_NOT_EMPTY(), notnull=True),
                Column('calcType', string, requires=IS_IN_SET(doseAnalysisType, error_message='Please select analysis type'), notnull=True, default=doseAnalysisType[0]),
                Column('nuc_owner', 'reference tbl_Radionuclides', notnull=True, ondelete='CASCADE', label='Radionuclide', represent = lambda v, r: v, requires=IS_IN_DB(db, 'tbl_Radionuclides', '%(name)s', error_message='Please select a radionuclide')),
                Column('activity', double, notnull=True, label = 'Activity', requires = IS_NOT_EMPTY(error_message='Please enter activity')),
                Column('intake', double, notnull=True, label = 'Intake', requires = IS_NOT_EMPTY(error_message='Please enter intake')),
                Column('ceffdose', double, notnull=True, label = 'Commulative Effective Dose', requires=IS_NOT_EMPTY(error_message='Please enter CED')),
                Column('dynamicMDA', double, notnull=True, default=0, label='MDA (Bq)', requires=IS_NOT_EMPTY(error_message='Please specify MDA')),
                Column('cpm', double, notnull=True, default=0, requires=IS_NOT_EMPTY(error_message='Please specify the cpm')),
                Column('monType', string, notnull=True, requires=IS_IN_SET(monType), label='Monitoring type', default = monType[0]),
                Column('intakeRoute', 'list:reference tbl_PossibleIntakeRoutes', requires=IS_IN_DB(db, 'tbl_PossibleIntakeRoutes.id', '%(description)s', multiple=True, error_message='Please select an intake route'), label='Intake routes', notnull=True),
                Column('radioClass', 'reference tbl_Classes', notnull=True, requires=IS_IN_DB(db, 'tbl_Classes', '%(name)s', error_message='Please specify class'), label='Class'),
                Column('comments', string),

                Column('retFraction', double, notnull=True, requires=IS_NOT_EMPTY(error_message = 'Retained fraction is required'), label='Retained fraction'),
                Column('doseCoeff', double, notnull=True, requires=IS_NOT_EMPTY(error_message = 'Dose coefficient is required'), label='Dose coefficient'),
                Column('effFactor', double, notnull=True, requires=IS_NOT_EMPTY(error_message = 'Efficiency Calibration Factor is required'), label='Efficiency calibration factor'),
                Column('intakeDate', datetime, label='Intake date'),

                Column('mowner', 'reference tbl_MonitoringDetails', notnull=True, ondelete='CASCADE', readable = False, writable = False),
                Column('deviceName', string, notnull=True, requires=IS_NOT_EMPTY()),        #   Extra 'resultant' for Resultant (sum) calculations
                auth.signature)


# RADIONUCLEID >>



db.define_table = Table('tbl_Radionuclides',metadata,
               Column('name', string, unique=True, notnull=True, requires=IS_NOT_IN_DB(db, 'tbl_Radionuclides.name', error_message='Name must not be empty and must not already exist')),
               Column('mda', double, notnull=True, requires=IS_NOT_EMPTY(), default=0, label='MDA'),
               Column('energy', double, notnull=True, requires=IS_NOT_EMPTY(), default = 0, label='Energy (keV)'),
               Column('myield', double, notnull=True, requires=IS_NOT_EMPTY(), default = 0, label='Yield'),
               auth.signature)
db.tbl_Radionuclides._after_insert.append(lambda f, id: db(db.tbl_CacheStatus.name == 'tbl_Radionuclides').update(lastUpdatedOn = request.now))
db.tbl_Radionuclides._after_update.append(lambda s, f:  db(db.tbl_CacheStatus.name == 'tbl_Radionuclides').update(lastUpdatedOn = request.now))




#   DOSE COEFFECIENT >>

db.define_table = Table('tbl_DoseCoeff',metadata,
                Column('nuclide', 'reference tbl_Radionuclides', notnull=True),
                Column('radioClass', 'reference tbl_Classes', notnull=True),
                Column('intakeRoute', 'reference tbl_PossibleIntakeRoutes', notnull=True),
                Column('doseCoeff', double, notnull=True),
                Column('dataSetId', 'reference tbl_DataSet', notnull=True),
                Column('created_on', 'datetime', notnull=True),
                Column('created_by', 'reference auth_user', notnull=True, ondelete='CASCADE'))
db.tbl_DoseCoeff._after_insert.append(lambda f, id: db(db.tbl_CacheStatus.name == 'tbl_DoseCoeff').update(lastUpdatedOn = request.now))
db.tbl_DoseCoeff._after_update.append(lambda s, f:  db(db.tbl_CacheStatus.name == 'tbl_DoseCoeff').update(lastUpdatedOn = request.now))

# DOSE CALCULATION >>
db.define_table = Table('tbl_DoseCalculations',metadata,
                Column('name', string, requires=IS_NOT_EMPTY(), notnull=True),
                Column('calcType', string, requires=IS_IN_SET(doseAnalysisType, error_message='Please select analysis type'), notnull=True, default=doseAnalysisType[0]),
                Column('nuc_owner', 'reference tbl_Radionuclides', notnull=True, ondelete='CASCADE', label='Radionuclide', represent = lambda v, r: v, requires=IS_IN_DB(db, 'tbl_Radionuclides', '%(name)s', error_message='Please select a radionuclide')),
                Column('activity', double, notnull=True, label = 'Activity', requires = IS_NOT_EMPTY(error_message='Please enter activity')),
                Column('intake', double, notnull=True, label = 'Intake', requires = IS_NOT_EMPTY(error_message='Please enter intake')),
                Column('ceffdose', double, notnull=True, label = 'Commulative Effective Dose', requires=IS_NOT_EMPTY(error_message='Please enter CED')),
                Column('dynamicMDA', double, notnull=True, default=0, label='MDA (Bq)', requires=IS_NOT_EMPTY(error_message='Please specify MDA')),
                Column('cpm', double, notnull=True, default=0, requires=IS_NOT_EMPTY(error_message='Please specify the cpm')),
                Column('monType', string, notnull=True, requires=IS_IN_SET(monType), label='Monitoring type', default = monType[0]),
                Column('intakeRoute', 'list:reference tbl_PossibleIntakeRoutes', requires=IS_IN_DB(db, 'tbl_PossibleIntakeRoutes.id', '%(description)s', multiple=True, error_message='Please select an intake route'), label='Intake routes', notnull=True),
                Column('radioClass', 'reference tbl_Classes', notnull=True, requires=IS_IN_DB(db, 'tbl_Classes', '%(name)s', error_message='Please specify class'), label='Class'),
                Column('comments', string),

                Column('retFraction', double, notnull=True, requires=IS_NOT_EMPTY(error_message = 'Retained fraction is required'), label='Retained fraction'),
                Column('doseCoeff', double, notnull=True, requires=IS_NOT_EMPTY(error_message = 'Dose coefficient is required'), label='Dose coefficient'),
                Column('effFactor', double, notnull=True, requires=IS_NOT_EMPTY(error_message = 'Efficiency Calibration Factor is required'), label='Efficiency calibration factor'),
                Column('intakeDate', datetime, label='Intake date'),

                Column('mowner', 'reference tbl_MonitoringDetails', notnull=True, ondelete='CASCADE', readable = False, writable = False),
                Column('deviceName', string, notnull=True, requires=IS_NOT_EMPTY()),        #   Extra 'resultant' for Resultant (sum) calculations
                auth.signature)

#SPECTRUM FILES >>

db.define_table = Table('tbl_OtherSpectrumFiles',metadata,
                Column('name', string, notnull=True),
                Column('contents', text, notnull=True),
                Column('fileType', string),
                Column('geometry', 'reference tbl_Geometry', notnull=True, ondelete='CASCADE'),
                Column('uniqueId', string, notnull=True, default='123e4567-e89b-12d3-a456-426655440000'),
                Column('created_on', datetime, notnull=True),
                Column('created_by', 'reference auth_user', notnull=True, ondelete='CASCADE'))
db.tbl_OtherSpectrumFiles._after_insert.append(lambda f, id: db(db.tbl_CacheStatus.name == 'tbl_OtherSpectrumFiles').update(lastUpdatedOn = request.now))
db.tbl_OtherSpectrumFiles._after_update.append(lambda s, f:  db(db.tbl_CacheStatus.name == 'tbl_OtherSpectrumFiles').update(lastUpdatedOn = request.now))



database = Database(DATABASE_URL)
metadata.create_all(engine)