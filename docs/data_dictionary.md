# Data Dictionary

## فیلدهای مشترک همه رکوردها

| فیلد | نوع | توضیح |
|------|-----|-------|
| id | string | یکتا، فرمت `dat_XX_NNNN` |
| category | string | دسته‌بندی داخلی دیتاست |
| source | object | {name, version, date, page, section, quote} |
| source_type | enum | primary / secondary / external |
| confidence | number | 0.0..1.0 |
| status | enum | complete / partial / unknown / inferred / blocked / deferred |
| conflicts | array | در صورت تعارض منابع |
| notes | string | توضیح |
| tags | array<string> | برچسب‌ها |
| applicable_models | array<string> | باید شامل `SIM800L` باشد |
| created_at | string(ISO 8601) | زمان ایجاد |
| updated_at | string(ISO 8601) | زمان آخرین به‌روزرسانی |

## فیلدهای اختصاصی (خلاصه)

- dat_01: command, mode, syntax, parameters, response_success, response_error, examples, related_urcs, related_states, related_commands, firmware_min, firmware_max
- dat_02: urc_string, trigger_event, related_command, related_state, format, parameters, examples, timing, suppression_method
- dat_03: error_type, code, meaning, description, related_commands, recovery_steps
- dat_04: parameter, min, typ, max, unit, condition, related_command, related_state, related_urc
- dat_05: state_name, description, entry_conditions, exit_conditions, events, actions, related_commands, related_urcs, related_timings
- dat_06: step_order, command, expected_response, timeout_ms, retry_count, failure_action, dependency_step, related_state
- dat_07: name, pin_number, direction, voltage_min/typ/max, current_typ/max, function, alternate_function, pull_up_down, esd_rating, impedance, decoupling
- dat_08: firmware_version, release_date, base_version, supported_commands, unsupported_commands, features, known_issues, fixed_issues, related_commands
- dat_09: mode, command, syntax, parameters, response, examples, related_urcs, encoding, storage, concat_sms, delivery_report
- dat_10: category, command, syntax, parameters, response, examples, related_urcs, related_states, related_commands
- dat_11: category, command, syntax, parameters, response, examples, related_urcs, related_commands
- dat_12: category, command, syntax, parameters, response, examples, related_commands
- dat_13: category, command, syntax, parameters, response, examples, related_urcs, hardware_pins
- dat_14: mcc, mnc, country, country_code, operator, brand, network_type, apn_list, source_url
- dat_15: category, mode, command, parameter, value_min/typ/max, unit, condition, wake_source, related_commands, related_states
- dat_16: category, name, connector, pin, function, voltage, notes
- dat_17: category, command, syntax, parameters, response, examples, tls_version, cipher_suite, cert_format, key_format, storage, limits, related_commands
- dat_18: certification_body, certificate_number, standard, country, date_issued, date_expiry, document_link, source
