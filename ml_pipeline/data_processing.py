# ml_pipeline/data_processing.py
import pandas as pd
import re
import difflib

def _normalize(name: str) -> str:
    if name is None:
        return ''
    name = str(name)
    name = name.strip().lower()
    # remove non-alphanumeric characters to improve matching ("preferred label" -> "preferredlabel")
    return re.sub(r'[^a-z0-9]+', '', name)

def _find_best_column(df: pd.DataFrame, expected: str) -> str | None:
    """
    Find the best matching column in df for the expected column name.
    Tries exact match, normalized match, then close match using difflib.
    """
    cols = list(df.columns)
    # 1) exact
    if expected in cols:
        return expected
    # 2) lower/strip normalized matches
    normalized_map = { _normalize(c): c for c in cols }
    norm_expected = _normalize(expected)
    if norm_expected in normalized_map:
        return normalized_map[norm_expected]
    # 3) difflib close match against normalized names
    candidates = list(normalized_map.keys())
    matches = difflib.get_close_matches(norm_expected, candidates, n=1, cutoff=0.6)
    if matches:
        return normalized_map[matches[0]]
    return None

def _ensure_and_rename(df: pd.DataFrame, required: list, df_name: str) -> pd.DataFrame:
    """
    Ensure df contains required columns by finding best matches and renaming them
    to the expected names. Raises ValueError if a required column can't be found.
    """
    mapping = {}
    for col in required:
        found = _find_best_column(df, col)
        if found is None:
            raise ValueError(f"Required column '{col}' not found (checked {df_name}). Available columns: {list(df.columns)[:10]}...")
        if found != col:
            mapping[found] = col
    if mapping:
        df = df.rename(columns=mapping)
        print(f"[fix] Renamed columns in {df_name}: {mapping}")
    return df

def _try_split_single_column(df: pd.DataFrame, expected_names: list, df_name: str) -> pd.DataFrame:
    """
    If df has a single column containing joined data, attempt to split it.
    After splitting:
      - If the first row looks like a header (contains expected names), set it as header and drop that row.
      - Otherwise, assign expected_names positionally to the first N columns and pad extras.
    """
    if df.shape[1] != 1:
        return df
    s = df.iloc[:, 0].astype(str)
    for sep in [';', '\t', '|', ',']:
        split = s.str.split(sep, expand=True)
        if split.shape[1] >= len(expected_names):
            # Inspect first row to see if it contains headers
            first_row = split.iloc[0].astype(str).tolist()
            normalized_first = [ _normalize(x) for x in first_row ]
            normalized_expected = [ _normalize(x) for x in expected_names ]
            # If any expected column name appears in the first row, treat it as header
            if any(ne in normalized_first for ne in normalized_expected):
                # Use the first row as header, then drop it
                split.columns = first_row
                split = split.drop(index=0).reset_index(drop=True)
                print(f"[fix] Split single-column {df_name} on '{sep}' and used first row as header.")
                return split
            # Otherwise, assign positional expected names to the leftmost columns
            cols = []
            for i in range(split.shape[1]):
                if i < len(expected_names):
                    cols.append(expected_names[i])
                else:
                    cols.append(f'__pad_{i - len(expected_names)}')
            split.columns = cols
            print(f"[fix] Split single-column {df_name} on '{sep}' and assigned positional column names.")
            return split
    return df

def _clean_quotes(s: str) -> str:
    if s is None:
        return ''
    s = str(s).strip()
    # remove wrapping double or single quotes
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    return s

def _find_uri_column(df: pd.DataFrame) -> str | None:
    """
    Return the first column name where many values look like ESCO occupation URIs.
    """
    uri_re = re.compile(r'https?://[^/]+/esco/(occupation|concept-scheme|occupation/)', re.IGNORECASE)
    for col in df.columns:
        sample = df[col].dropna().astype(str).head(50).tolist()
        if not sample:
            continue
        matches = sum(bool(uri_re.search(x)) for x in sample)
        if matches >= max(1, len(sample)//5):  # heuristic: at least 20% or >=1 matches
            return col
    return None

def _find_short_text_column(df: pd.DataFrame, candidates: list) -> str | None:
    """
    Pick the best column for a short label/title among candidates or all columns:
    heuristic = median token length <= 6 and many non-empty values.
    """
    cols_to_check = candidates if candidates else list(df.columns)
    best = None
    for col in cols_to_check:
        s = df[col].dropna().astype(str)
        if s.empty:
            continue
        word_counts = s.str.split().str.len()
        median_wc = int(word_counts.median()) if not word_counts.empty else 999
        non_empty_ratio = len(s) / max(1, len(df))
        # prefer short median and reasonably populated column
        if median_wc <= 6 and non_empty_ratio >= 0.1:
            return col
        if best is None or median_wc < best[1]:
            best = (col, median_wc)
    return best[0] if best else None

def clean_and_merge_data(raw_data: dict) -> pd.DataFrame:
    print("Starting data cleaning and preparation...")
    
    # <-- REPLACED: use the full ESCO positional column list for occupations -->
    OCC_COLS = [
        'conceptType', 'conceptUri', 'iscoGroup', 'preferredLabel',
        'altLabels', 'hiddenLabels', 'status', 'modifiedDate',
        'regulatedProfessionNote', 'scopeNote', 'definition', 'inScheme',
        'description', 'code'
    ]
    # Skills file: keep conceptUri and preferredLabel present and positional mapping stable
    SKILL_COLS = [
        'conceptType', 'conceptUri', 'skillType', 'reuseLevel',
        'preferredLabel', 'altLabels', 'hiddenLabels', 'status',
        'modifiedDate', 'scopeNote', 'definition', 'inScheme',
        'description', 'code'
    ]
    REL_COLS = ['occupationUri', 'relationType', 'skillType', 'skillUri']
    
    # Defensive: if any DF is a single concatenated column, try splitting
    for k, expected in [('occupations', OCC_COLS), ('skills', SKILL_COLS), ('relations', REL_COLS)]:
        if raw_data[k].shape[1] == 1:
            raw_data[k] = _try_split_single_column(raw_data[k], expected, df_name=k)
    
    # Aggressive header cleanup: strip control chars and normalize whitespace
    for k, df in raw_data.items():
        cleaned = [ re.sub(r'[\r\n\x00-\x1F\x7F]', '', str(c)).strip() for c in df.columns ]
        raw_data[k].columns = cleaned

    # Ensure and rename required columns (will raise with clear message if missing)
    try:
        raw_data['occupations'] = _ensure_and_rename(raw_data['occupations'], OCC_COLS, 'occupations')
        raw_data['skills'] = _ensure_and_rename(raw_data['skills'], SKILL_COLS, 'skills')
        raw_data['relations'] = _ensure_and_rename(raw_data['relations'], REL_COLS, 'relations')
    except ValueError as e:
        # Surface a clear error to the caller/run_pipeline
        raise Exception(str(e))
    
    # --- 1. Clean Skills Data ---
    skills_df = raw_data['skills'].copy()
    skills_df = skills_df[['conceptUri', 'preferredLabel']].rename(
        columns={'conceptUri': 'skillUri', 'preferredLabel': 'skill_name'}
    )
    skills_df['skill_name'] = skills_df['skill_name'].astype(str).str.lower().str.strip()

    # --- 2. Clean Relations Data ---
    relations_df = raw_data['relations'].copy()
    relations_df = relations_df[['occupationUri', 'skillUri']]

    # --- 3. Merge Skills into Relations ---
    skill_relations_df = pd.merge(
        relations_df,
        skills_df,
        on='skillUri',
        how='left'
    )
    
    # --- 4. Group Skills by Occupation ---
    occupation_skills = skill_relations_df.groupby('occupationUri')['skill_name'].apply(
        lambda x: ' '.join(x.dropna().astype(str))
    ).reset_index(name='aggregated_skills')

    # --- 5. Clean Occupations Data and Final Merge ---
    occupations_df = raw_data['occupations'].copy()
    occupations_df['description'] = occupations_df.get('description', '').fillna('')
    occupations_df['definition'] = occupations_df.get('definition', '').fillna('')
    
    final_df = pd.merge(
        occupations_df,
        occupation_skills,
        left_on='conceptUri',
        right_on='occupationUri',
        how='left'
    )
    
    # --- 6. Create the Unified Embedding Text ---
    final_df['text_for_embedding'] = (
        final_df['preferredLabel'].astype(str).str.lower() + ". " + 
        final_df['description'].astype(str).str.lower() + ". " + 
        final_df['definition'].astype(str).str.lower() + ". " + 
        final_df['aggregated_skills'].fillna('').astype(str).str.lower()
    )
    
    # --- SANITIZATION: ensure correct URI and short title are used ---
    # If conceptUri or preferredLabel look wrong, try to recover from other columns.
    # Look for a column containing occupation URIs
    uri_col = _find_uri_column(occupations_df)
    if uri_col:
        final_df['conceptUri'] = occupations_df[uri_col].astype(str).apply(_clean_quotes)
        if uri_col != 'conceptUri':
            print(f"[fix] Replaced conceptUri using detected URI column: {uri_col}")

    # Find a short title column candidate (prefer 'preferredLabel' then 'preferredlabel' variants)
    title_candidates = [c for c in occupations_df.columns if _normalize(c).find('preferred') != -1] + list(occupations_df.columns)
    title_col = _find_short_text_column(occupations_df, title_candidates)
    if title_col:
        final_df['preferredLabel'] = occupations_df[title_col].astype(str).apply(_clean_quotes)
        if title_col != 'preferredLabel':
            print(f"[fix] Replaced preferredLabel using detected title column: {title_col}")

    # Final defensive cleanup: strip surrounding quotes from both fields
    final_df['conceptUri'] = final_df['conceptUri'].astype(str).apply(_clean_quotes)
    final_df['preferredLabel'] = final_df['preferredLabel'].astype(str).apply(_clean_quotes)

    # Keep only the expected final columns
    final_df = final_df[['conceptUri', 'preferredLabel', 'text_for_embedding']].copy()

    print(f"Data processing complete. Final DataFrame size: {len(final_df)} rows.")
    return final_df