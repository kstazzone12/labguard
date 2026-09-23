import { beforeEach, describe, expect, it } from "vitest";
import { clearProfessionalData, createRecord, deleteRecord, getRecordById, getRecords, updateRecord } from "./localData";
import { emptyDraft, validateDraft } from "./professionalRecords";

const storage = new Map<string, string>();
Object.defineProperty(globalThis, "localStorage", { value: {
  getItem: (key: string) => storage.get(key) ?? null,
  setItem: (key: string, value: string) => storage.set(key, value),
  removeItem: (key: string) => storage.delete(key),
  clear: () => storage.clear(),
} });

const validDraft = {
  ...emptyDraft, previous_value: "5.0", previous_date: "2026-01-14",
  patient_id: "patient-local-1", sample_id: "sample-local-1", date: "2026-01-15", time: "08:30", analyte: "glucose", value: "5.2", unit: "mmol/L", specimen: "serum", method: "method-1", instrument: "instrument-1", qc_status: "accepted",
};

describe("professional records", () => {
  beforeEach(() => { storage.clear(); });

  it("validates and creates a row", () => {
    const result = validateDraft(validDraft, []);
    expect(result.level).toBe("VALID");
    const record = createRecord(result.record!);
    expect(getRecordById(record.id)?.sample_id).toBe("sample-local-1");
  });

  it("rejects duplicate sample ids and invalid values", () => {
    const first = createRecord(validateDraft(validDraft, []).record!);
    const duplicate = validateDraft({ ...validDraft, value: "not-number" }, [first]);
    expect(duplicate.level).toBe("ERROR");
    expect(duplicate.issues.map((item) => item.code)).toEqual(expect.arrayContaining(["DUPLICATE_SAMPLE_ID", "INVALID_NUMERIC_VALUE"]));
  });

  it("does not warn for optional delta and QC context", () => {
    const warning = validateDraft({ ...validDraft, previous_value: "", previous_date: "", qc_status: "" }, []);
    expect(warning.level).toBe("VALID");
    expect(warning.record).toBeDefined();
    const error = validateDraft({ ...validDraft, date: "2026-02-31" }, []);
    expect(error.level).toBe("ERROR");
    expect(error.record).toBeUndefined();
  });

  it("normalizes common laboratory date and QC formats", () => {
    const result = validateDraft({ ...validDraft, date: "15/01/2026", previous_date: "14/01/2026", qc_status: "OK" }, []);
    expect(result.level).toBe("VALID");
    expect(result.record?.date).toBe("2026-01-15");
    expect(result.record?.qc_status).toBe("accepted");
  });

  it("reports a warning only when QC explicitly requires review", () => {
    const result = validateDraft({ ...validDraft, qc_status: "review_required" }, []);
    expect(result.level).toBe("WARNING");
    expect(result.issues.map((item) => item.code)).toContain("QC_REVIEW_REQUIRED");
  });

  it("updates, persists, deletes and clears records", () => {
    const record = createRecord(validateDraft(validDraft, []).record!);
    updateRecord({ ...record, value: 6.1 });
    expect(getRecords()[0].value).toBe(6.1);
    expect(getRecordById(record.id)?.value).toBe(6.1);
    deleteRecord(record.id);
    expect(getRecords()).toHaveLength(0);
    createRecord(validateDraft(validDraft, []).record!);
    clearProfessionalData();
    expect(getRecords()).toHaveLength(0);
  });
});
