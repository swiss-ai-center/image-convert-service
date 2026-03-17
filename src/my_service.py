from common_code.config import get_settings
from common_code.logger.logger import get_logger, Logger
from common_code.service.models import Service
from common_code.service.enums import ServiceStatus
from common_code.common.enums import FieldDescriptionType, ExecutionUnitTagName, ExecutionUnitTagAcronym
from common_code.common.models import FieldDescription, ExecutionUnitTag
from common_code.tasks.models import TaskData
# Imports required by the service's model
import io
from PIL import Image

api_description = """
This service converts images from different formats to different formats.
Acceptable formats are: image/png, image/jpeg.
"""
api_summary = """
Converts image between image/png and image/jpeg formats.
"""

api_title = "Image Convert API."
version = "0.0.1"

settings = get_settings()


class MyService(Service):
    """
    Image convert model
    """

    # Any additional fields must be excluded for Pydantic to work
    _model: object
    _logger: Logger

    def __init__(self):
        super().__init__(
            name="Image Convert",
            slug="image-convert",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            data_in_fields=[
                FieldDescription(name="image", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
                FieldDescription(name="format", type=[FieldDescriptionType.TEXT_PLAIN]),
            ],
            data_out_fields=[
                FieldDescription(name="result", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]),
            ],
            tags=[
                ExecutionUnitTag(
                    name=ExecutionUnitTagName.IMAGE_PROCESSING,
                    acronym=ExecutionUnitTagAcronym.IMAGE_PROCESSING
                ),
            ],
            has_ai=False,
            docs_url="https://docs.swiss-ai-center.ch/reference/services/image-convert/",
        )
        self._logger = get_logger(settings)

    def get_output_types(self):
        return self.data_out_fields[0]["type"]

    def process(self, data):
        raw = data["image"].data
        input_type = data["image"].type
        output_type = data["format"].data.decode("utf-8")

        # output_type to FieldDescriptionType
        output_type_fd = FieldDescriptionType(output_type)

        if input_type == output_type_fd:
            return {
                "result": TaskData(
                    data=raw,
                    type=output_type,
                )
            }
        service = MyService()
        if output_type_fd not in service.get_output_types():
            raise Exception("Output type not supported.")

        stream = io.BytesIO(raw)
        img = Image.open(stream)
        img = img.convert("RGB")

        out_buff = io.BytesIO()
        img.save(out_buff, format=output_type.split('/')[1])
        out_buff.seek(0)
        return {
            "result": TaskData(
                data=out_buff.read(),
                type=output_type,
            )
        }
