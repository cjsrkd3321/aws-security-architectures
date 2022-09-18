from libs.utils import stream_to_str, convert_center_string_to_asterisk


def get_detect_result_from_sensitive_result(s3, affected_object_path, result):
    detect_results = []
    custom_detections, sensitive_data = [
        result["customDataIdentifiers"]["detections"],
        result["sensitiveData"],
    ]
    if not (custom_detections or sensitive_data):
        return

    if custom_detections:
        for detection in custom_detections:
            name = detection["name"]
            occurrences = detection["occurrences"]
            detect_results.append(
                get_private_info_from_object(
                    s3=s3,
                    object=affected_object_path,
                    occurrences=occurrences,
                    type_=name,
                )
            )

    # AWS MANAGED RULE (https://docs.aws.amazon.com/ko_kr/macie/latest/user/managed-data-identifiers.html)
    if sensitive_data:
        sensitive_data_results = [
            (sensitive_datum["category"], sensitive_datum["detections"])
            for sensitive_datum in sensitive_data
        ]
        for category, detections in sensitive_data_results:
            for detection in detections:
                detection_type = detection["type"]
                occurrences = detection["occurrences"]
                detect_results.append(
                    get_private_info_from_object(
                        s3=s3,
                        object=affected_object_path,
                        occurrences=occurrences,
                        category=category,
                        type_=detection_type,
                    )
                )
                
    return detect_results


# https://docs.aws.amazon.com/ko_kr/macie/latest/user/findings-locate-sd-schema.html
def get_private_info_from_object(s3, object, occurrences, type_, category="CUSTOM"):
    splited_object = object.split("/")
    bucket_name, key = [splited_object[0], "/".join(splited_object[1:])]

    body = stream_to_str(
        s3.get_object(
            Bucket=bucket_name,
            Key=key,
        )["Body"]
    )

    results = {}
    result_key = f"{type_}|{category}|{object}"

    if occurrences.get("cells"):
        results[result_key] = occurrences["cells"]
    if occurrences.get("lineRanges"):
        results[result_key] = []
        for line_range in occurrences["lineRanges"]:
            [start, end, start_column] = [
                (int(line_range[key]) - 1) for key in ["start", "end", "startColumn"]
            ]
            sensitive_columns = "".join(body.split("\n")[start : end + 1])
            results[result_key] += [
                convert_center_string_to_asterisk(sensitive_columns[start_column:start_column + 100])
            ]
    elif occurrences.get("pages"):
        results[result_key] = occurrences["pages"]
    elif occurrences.get("records"):
        results[result_key] = occurrences["records"]
    elif occurrences.get("offsetRanges"):
        #  This array is reserved for future use. If this array is present, the value for it is always null.
        pass

    return results
