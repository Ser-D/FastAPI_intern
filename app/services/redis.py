import csv
import io
import json
import os

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.db.redis import redis_client


class RedisService:
    @staticmethod
    async def get_user_quiz_responses(quiz_id: int, user_id: int) -> list:
        if quiz_id:
            key = f"quiz_responses:{user_id}:{quiz_id}"
            data = await redis_client.get(key)
            if not data:
                raise HTTPException(
                    status_code=404,
                    detail="No quiz responses found for this user and quiz.",
                )
            return json.loads(data)
        else:
            pattern = f"quiz_responses:{user_id}:*"
            keys = await redis_client.keys(pattern)
            results = []
            for key in keys:
                data = await redis_client.get(key)
                if data:
                    results.append(json.loads(data))
            if not results:
                raise HTTPException(
                    status_code=404, detail="No quiz responses found for this user."
                )
            return results

    @staticmethod
    async def get_company_quiz_responses(
        quiz_id: int, company_id: int, user_id: int = None
    ) -> list:
        results = []

        pattern = f"quiz_responses:*:{quiz_id}"
        keys = await redis_client.keys(pattern)

        for key in keys:
            data = await redis_client.get(key)
            if data:
                quiz_responses = json.loads(data)
                if quiz_responses[3]["quiz_data"]["company_id"] == company_id:
                    if user_id:
                        if quiz_responses[3]["quiz_data"]["user_id"] == user_id:
                            results.extend(quiz_responses)
                    else:
                        results.extend(quiz_responses)

        if not results:
            raise HTTPException(
                status_code=404,
                detail="No quiz responses found for this user and quiz.",
            )
        return results

    @staticmethod
    def export_quiz_results(
        results: list, format: str, save_path: str
    ) -> StreamingResponse:
        quiz_data_list = [
            result["quiz_data"] for result in results if "quiz_data" in result
        ]

        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow(quiz_data_list[0].keys())

            for data in quiz_data_list:
                writer.writerow(data.values())
            output.seek(0)
            RedisService.save_file(output.getvalue(), "quiz_results.csv", save_path)
            return StreamingResponse(
                output,
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=quiz_results.csv"
                },
            )
        else:
            output = io.StringIO()
            json.dump(quiz_data_list, output)
            output.seek(0)
            RedisService.save_file(output.getvalue(), "quiz_results.json", save_path)
            return StreamingResponse(
                output,
                media_type="application/json",
                headers={
                    "Content-Disposition": "attachment; filename=quiz_results.json"
                },
            )

    @staticmethod
    def save_file(content: str, filename: str, directory: str):
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, filename)
        with open(file_path, "w") as f:
            f.write(content)


redis_service = RedisService()
