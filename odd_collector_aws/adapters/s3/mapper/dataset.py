from typing import Dict, List, Any

from odd_models.models import DataSetField, Type, DataSetFieldType, DataEntity, DataSet, DataEntityType
from oddrn_generator.generators import S3Generator
from pyarrow import Field, Schema, lib

SCHEMA_FILE_URL = "https://raw.githubusercontent.com/opendatadiscovery/opendatadiscovery-specification/" \
                  "main/specification/extensions/s3.json"

TYPE_MAP: Dict[str, Type] = {
    'int8': Type.TYPE_INTEGER,
    'int16': Type.TYPE_INTEGER,
    'int32': Type.TYPE_INTEGER,
    'int64': Type.TYPE_INTEGER,
    'uint8': Type.TYPE_INTEGER,
    'uint16': Type.TYPE_INTEGER,
    'uint32': Type.TYPE_INTEGER,
    'uint64': Type.TYPE_INTEGER,
    'float8': Type.TYPE_NUMBER,
    'float16': Type.TYPE_NUMBER,
    'float32': Type.TYPE_NUMBER,
    'float64': Type.TYPE_NUMBER,
    'time32': Type.TYPE_TIME,
    'time64': Type.TYPE_TIME,
    'timestamp': Type.TYPE_DATETIME,
    'date32': Type.TYPE_DATETIME,
    'date64': Type.TYPE_DATETIME,
    'duration': Type.TYPE_DURATION,
    'month_day_nano_interval': Type.TYPE_DURATION,
    'binary': Type.TYPE_BINARY,
    'string': Type.TYPE_STRING,
    'utf8': Type.TYPE_STRING,
    'large_binary': Type.TYPE_BINARY,
    'large_string': Type.TYPE_STRING,
    'large_utf8': Type.TYPE_STRING,
    'decimal128': Type.TYPE_NUMBER,
    lib.ListType: Type.TYPE_LIST,
    lib.StructType: Type.TYPE_STRUCT,
}


def map_dataset(name, schema: Schema, metadata: Dict, oddrn_gen: S3Generator) -> DataEntity:
    name = ':'.join(name.split('/')[1:])

    oddrn_gen.set_oddrn_paths(keys=name)
    rows = metadata['Rows']
    del metadata['Rows']
    metadata = [{'schema_url': f'{SCHEMA_FILE_URL}#/definitions/GlueDataSetExtension',
                'metadata': metadata}]

    return DataEntity(
        name=name,
        oddrn=oddrn_gen.get_oddrn_by_path('keys', name),
        metadata=metadata,
        # TODO
        updated_at=None,
        created_at=None,
        type=DataEntityType.FILE,
        dataset=DataSet(
            rows_number=rows,
            field_list=map_columns(schema, oddrn_gen)
        )
    )


def map_column(field: Field, oddrn_gen: S3Generator) -> DataSetField:
    return DataSetField(
        name=field.name,
        oddrn=oddrn_gen.get_oddrn_by_path('columns', field.name),
        type=DataSetFieldType(
            type=TYPE_MAP.get(str(field.type), TYPE_MAP.get(type(field.type), Type.TYPE_UNKNOWN)),
            logical_type=str(field.type),
            is_nullable=field.nullable
        )
    )


def map_columns(schema: Schema, oddrn_gen: S3Generator) -> List[DataSetField]:
    return [
        map_column(field=schema.field(i), oddrn_gen=oddrn_gen)
        for i in range(0, len(schema))
    ]
