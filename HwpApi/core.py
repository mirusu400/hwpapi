# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_api/00_core.ipynb.

# %% auto 0
__all__ = ['mask_options', 'scan_spos_keys', 'scan_epos_keys', 'scan_directions', 'move_ids', 'size_options', 'effects',
           'directions', 'App', 'move_to_line']

# %% ../nbs/02_api/00_core.ipynb 4
from pathlib import Path
from fastcore.basics import patch
from contextlib import contextmanager

# %% ../nbs/02_api/00_core.ipynb 5
from .actions import _Actions, _Action
from .functions import dispatch, get_absolute_path, check_dll, get_value, set_charshape_pset, set_parashape_pset, hex_to_rgb

# %% ../nbs/02_api/00_core.ipynb 6
class App:
    ''' App 클래스는 한컴오피스의 한/글 프로그램과 상호작용하기 위한 인터페이스를 제공합니다.'''
    def __init__(self, api=None):
        ''' `__init__` 함수에서는 `api` 객체를 인자로 받습니다. 
        만약 `api`가 제공되지 않았을 경우, `wc.gencache.EnsureDispatch("HWPFrame.HwpObject")`를 호출하여 
        기본값으로 한/글 프로그램의 COM 객체를 생성합니다. 그리고 `self.api` 속성에 이 객체를 할당합니다. 
        `_Actions` 클래스의 객체를 생성하여 `self.actions` 속성에 할당하고, `self.set_visible()` 함수를 호출합니다.'''
        if not api:        
            api = dispatch("HWPFrame.HwpObject")
        self.api = api
        self.actions = _Actions(self)
        self.parameters = api.HParameterSet
        self.set_visible()
        check_dll()
        self.api.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
                
    def __str__(self): return f"<Hwp App: {self.get_filepath()}>"
    __repr__ = __str__

# %% ../nbs/02_api/00_core.ipynb 7
@patch
def set_visible(app:App, is_visible=True, window_i=0):
    '''`set_visible()` 함수는 한/글 프로그램의 창을 화면에 보이거나 숨기기 위해 호출됩니다. 
    `is_visible` 인자가 `True`일 경우 창이 화면에 보이고, `False`일 경우 숨깁니다. 
    `window_i` 인자는 창의 인덱스를 지정합니다.'''

    app.api.XHwpWindows.Item(window_i).Visible = is_visible

# %% ../nbs/02_api/00_core.ipynb 8
@patch
def get_filepath(app:App):
    '''`get_filepath()` 함수는 현재 열려있는 한/글 문서의 경로를 반환합니다.'''
    doc = app.api.XHwpDocuments.Active_XHwpDocument
    return doc.FullName

# %% ../nbs/02_api/00_core.ipynb 10
@patch
def open(app:App, path:str):
    '''`open()` 함수는 파일 경로를 인자로 받아 해당 파일을 한/글 프로그램에서 엽니다. 
    `get_absolute_path()` 함수를 호출하여 절대 경로로 변환한 후, `api.Open()` 함수를 호출하여 파일을 엽니다. 
    열린 파일의 경로를 반환합니다.'''
    name = get_absolute_path(path)
    app.api.Open(name)
    return name

# %% ../nbs/02_api/00_core.ipynb 12
@patch
def save(app:App, path=None):
    '''`save()` 함수는 현재 열려있는 문서를 저장하거나 다른 이름으로 저장합니다. 
    `path` 인자가 주어지지 않은 경우 현재 문서를 덮어쓰기로 저장하고, 저장된 파일의 경로를 반환합니다. 
    `path` 인자가 주어진 경우, `Path` 모듈을 이용하여 파일 확장자를 추출한 후, 해당 확장자에 맞게 문서를 저장합니다. 
    저장된 파일의 경로를 반환합니다.'''

    if not path:
        app.api.Save()
        return app.get_filepath()
    name = get_absolute_path(path)
    extension = Path(name).suffix
    format_ = {".hwp": "HWP", ".pdf": "PDF", ".hwpx": "HWPML2X"}.get(extension)

    app.api.SaveAs(name, format_)
    return name

# %% ../nbs/02_api/00_core.ipynb 13
@patch
def close(app:App):
    '''`close()` 함수는 현재 열려있는 문서를 닫습니다.'''
    app.api.Run("FileClose")

# %% ../nbs/02_api/00_core.ipynb 14
@patch
def quit(app:App):
    '''`quit()` 함수는 한/글 프로그램을 종료합니다.'''
    app.api.Run("FileQuit")

# %% ../nbs/02_api/00_core.ipynb 15
@patch        
def create_action(app:App, action_key:str):
    '''`create_action()` 함수는 `_Action` 클래스의 객체를 생성하여 반환합니다.'''
    return _Action(app, action_key)

# %% ../nbs/02_api/00_core.ipynb 16
@patch    
def create_parameterset(app:App, action_key:str):
    '''`create_parameterset()` 함수는 특정 액션의 파라미터셋을 반환합니다.
    `_action_info` 딕셔너리에서 액션에 대한 정보를 찾아서 파라미터셋의 키 값을 가져옵니다. 파라미터셋 객체를 반환합니다.'''
    pset_key, description = _action_info.get(action_key, None)
    if not pset_key:
        return None
    return getattr(app.api.HParameterSet, f"H{pset_key}")


# %% ../nbs/02_api/00_core.ipynb 17
@patch
def set_charshape(app:App, 
    fontname:str=None, 
    font_type:int=1, 
    size:int=None,
    ratio:int=None, 
    spacing:int=None, 
    offset:int=None,
    bold:bool=None, 
    italic:bool=None, 
    small_caps:bool=None,
    emboss:bool=None,
    super_script:bool=None,
    sub_script:bool=None,
    underline_type:int=None,
    outline_type:int=None,
    text_color=None,
    shade_color=None,
    underline_shape:int=None,
    underline_color=None,
    shadow_offset_x:int=None,
    shadow_offset_y:int=None,
    shadow_color=None,
    strike_out_type=None,
    diac_sym_mark=None,
    use_font_space=None,
    use_kerning=None,
    height:int=None,):
    '''`현재 위치의 글자 모양을 조정합니다.'''
    charshape = app.actions.CharShape()
    
    if height:
        height = app.api.PointToHwpUnit(height)
    
    if text_color:
        text_color = app.api.RGBColor(*hex_to_rgb(text_color))
    if shade_color:
        shade_color = app.api.RGBColor(*hex_to_rgb(shade_color))
    if shadow_color:
        shadow_color = app.api.RGBColor(*hex_to_rgb(shadow_color))
        
    
    set_charshape_pset(charshape.pset, 
        face_name=fontname, 
        font_type=font_type,
        size=size,
        ratio=ratio,
        spacing=spacing,
        offset=offset,
        bold=bold,
        italic=italic,
        small_caps=small_caps,
        emboss=emboss,
        super_script=super_script,
        sub_script=sub_script,
        underline_type=underline_type,
        outline_type=outline_type,
        text_color=text_color,
        shade_color=shade_color,
        underline_shape=underline_shape,
        underline_color=underline_color,
        shadow_offset_x=shadow_offset_x,
        shadow_offset_y=shadow_offset_y,
        shadow_color=shadow_color,
        strike_out_type=strike_out_type,
        diac_sym_mark=diac_sym_mark,
        use_font_space=use_font_space,
        use_kerning=use_kerning,
        height=height,   # 포인트를 한글 유닛으로 변경합니다.
    )
    return charshape.run()

# %% ../nbs/02_api/00_core.ipynb 18
@patch
def set_parashape(app:App,
    left_margin:int=None,
    right_margin:int=None,
    indentation:int=None,
    prev_spacing:int=None,
    next_spacing:int=None,
    line_spacing_type:str=None,
    line_spacing:int=None,
    align_type:str=None,
    break_latin_word:str=None,
    break_non_latin_word:bool=None,
    snap_to_grid:bool=None,
    condense:float=None,
    widow_orphan:bool=None,
    keep_with_next:bool=None,
    page_break_before:bool=None,
    text_alignment:str=None,
    font_line_height:int=None,
    heading_type:str=None,
    level:int=None,
    border_connect:bool=None,
    border_text:bool=None,
    border_offset_left:int=None,
    border_offset_right:int=None,
    border_offset_top:int=None,
    border_offset_bottom:int=None,
    tail_type:bool=None,
    line_wrap:bool=None,
    tab_def=None,
    numbering=None,
    bullet=None,
    borderfill=None):
    
    parashape = app.actions.ParagraphShape()
    
    # enum 스타일
    spacing_types = {
        "Word": 0,
        "Fixed": 1,
        "Margin": 2,
    }
    if line_spacing_type:
        line_spacing_type = get_value(spacing_types, line_spacing_type)
    
    align_types = {
        "Both" : 0,
        "Left": 1,
        "Right": 2, 
        "Center": 3,
        "Distributed": 4,
        "SpaceOnly": 5,
    }
    if align_type:
        align_type = get_value(align_types, align_type)
    
    break_latin_words = {
        "Word": 0,
        "Hyphen":1,
        "Letter":2,
    }
    if break_latin_word:
        break_latin_word = get_value(break_latin_words, break_latin_word)
    
    text_alignments = {
        "Font": 0,
        "Upper": 1,
        "Middle": 2,
        "Lower": 3,
    }
    if text_alignment:
        text_alignment = get_value(text_alignments, text_alignment)
    
    heading_types = {
        "None": 0,
        "Content": 1,
        "Numbering": 2,
        "Bullet": 3,
    }
    if heading_type:
        heading_type = get_value(heading_types, heading_type)
    
    # 유닛 조정
    mili_units = [border_offset_left, border_offset_right, border_offset_top, border_offset_bottom]
    convert_mili = lambda value : app.api.MiliToHwpUnit(value) if value else None
    mili_units = list(map(convert_mili, mili_units))
    border_offset_left, border_offset_right, border_offset_top, border_offset_bottom = mili_units
    
    point_units = [left_margin, right_margin] 
    convert_point = lambda value : app.api.PointToHwpUnit(value)*2 if value else None
    point_units = list(map(convert_point, point_units))
    left_margin, right_margin = point_units
    
    
    set_parashape_pset(
        parashape.pset,
        left_margin=left_margin,
        right_margin=right_margin,
        indentation=indentation,
        prev_spacing=prev_spacing,
        next_spacing=next_spacing,
        line_spacing_type=line_spacing_type,
        line_spacing=line_spacing,
        align_type=align_type,
        break_latin_word=break_latin_word,
        break_non_latin_word=break_non_latin_word,
        snap_to_grid=snap_to_grid,
        condense=condense,
        widow_orphan=widow_orphan,
        keep_with_next=keep_with_next,
        page_break_before=page_break_before,
        text_alignment=text_alignment,
        font_line_height=font_line_height,
        heading_type=heading_type,
        level=level,
        border_connect=border_connect,
        border_text=border_text,
        border_offset_left=border_offset_left,
        border_offset_right=border_offset_right,
        border_offset_top=border_offset_top,
        border_offset_bottom=border_offset_bottom,
        tail_type=tail_type,
        line_wrap=line_wrap,
    )
    
    return parashape.run()
        

# %% ../nbs/02_api/00_core.ipynb 19
@patch
def insert_text(app:App, text:str, fontname=None, font_type=1, bold=None, italic=None, strike_out_type=None, underline_type=None, ratio=None, height=None, text_color=None):
    '''`text를 입력합니다.'''
    app.set_charshape(fontname=fontname, font_type=font_type, bold=bold, italic=italic, strike_out_type=strike_out_type, underline_type=underline_type, ratio=ratio, height=height, text_color=text_color)
    insert_text = app.actions.InsertText()
    p = insert_text.pset
    p.Text = text
    insert_text.run()
    return 

# %% ../nbs/02_api/00_core.ipynb 24
mask_options = {
    "Normal": 0x00,         # "본문을 대상으로 검색한다.(서브리스트를 검색하지 않는다.)"
    "Char": 0x01,           # "char 타입 컨트롤 마스크를 대상으로 한다.(강제줄나눔, 문단 끝, 하이픈, 묶움빈칸, 고정폭빈칸, 등...)"
    "Inline": 0x02,         # "inline 타입 컨트롤 마스크를 대상으로 한다.(누름틀 필드 끝, 등...)"
    "Ctrl": 0x04,           # "extende 타입 컨트롤 마스크를 대상으로 한다.(바탕쪽, 프레젠테이션, 다단, 누름틀 필드 시작, Shape Object, 머리말, 꼬리말, 각주, 미주, 번호관련 컨트롤, 새 번호 관련 컨트롤, 감추기, 찾아보기, 글자 겹침, 등...)"
    "All": None
}

scan_spos_keys = {
    "Current": 0x0000,      # "캐럿 위치부터. (시작 위치)",
    "Specified": 0x0010,    # "특정 위치부터. (시작 위치)",
    "Line": 0x0020,         # "줄의 시작부터. (시작 위치)",
    "Paragraph": 0x0030,    # "문단의 시작부터. (시작 위치)"
    "Section": 0x0040,      # "구역의 시작부터. (시작 위치)"
    "List": 0x0050,         # "리스트의 시작부터. (시작 위치)"
    "Control": 0x0060,      # "컨트롤의 시작부터. (시작 위치)"
    "Document": 0x0070,     # "문서의 시작부터. (시작 위치)"
}

scan_epos_keys = {
    "Current": 0x0000,      # "캐럿 위치까지. (끝 위치)"
    "Specified": 0x0001,    # "특정 위치까지. (끝 위치)"
    "Line": 0x0002,         # "줄의 끝까지. (끝 위치)"
    "Paragraph": 0x0003,    # "문단의 끝까지. (끝 위치)"
    "Section": 0x0004,      # "구역의 끝까지. (끝 위치)"
    "List": 0x0005,         # "리스트의 끝까지. (끝 위치)"
    "Control": 0x0006,      # "컨트롤의 끝까지. (끝 위치)"
    "Document": 0x0007,     # "문서의 끝까지. (끝 위치)"
}

scan_directions = {
    "Forward": 0x0000, # "정뱡향. (검색 방향)"
    "Backward": 0x0100  # "역방향. (검색 방향)"
}


def _get_text(app):
    """스캔한 텍스트 텍스트 제너레이터"""
    flag, text = 2, ""
    while flag not in [0, 1, 101, 102]:
        flag, text = app.api.GetText()
        yield text

@patch
@contextmanager
def scan(app:App, option="All", selection=False, scan_spos="Document", scan_epos="Document", spara=None, spos=None, epara=None, epos=None, scan_direction="Forward"):
    
    # set start and end position
    spos_id = get_value(scan_spos_keys, scan_spos)
    epos_id = get_value(scan_epos_keys, scan_epos)
    range_ = spos_id + epos_id
    # if selection
    if selection:
        range_ = 0x00ff    # "검색의 범위를 블록으로 제한."
    
    # set direction
    direction = get_value(scan_directions, scan_direction)
    range_ = range_ + direction
    app.api.InitScan(option=get_value(mask_options, option), Range=range_, spara=spara, spos=spos, epara=epara, epos=epos)
    yield _get_text(app)   
    app.api.ReleaseScan()

# %% ../nbs/02_api/00_core.ipynb 25
def move_to_line(app:App, text):
    """인자로 전달한 텍스트가 있는 줄의 시작지점으로 이동합니다."""
    with app.scan(scan_spos="Line") as scan:
        for line in scan:
            if text in line:
                return app.move()
    return False

# %% ../nbs/02_api/00_core.ipynb 26
move_ids = {
    "Main": 0,    # 루트 리스트의 특정 위치.(para pos로 위치 지정)
    "CurList": 1,    # 현재 리스트의 특정 위치.(para pos로 위치 지정)
    "TopOfFile": 2,   #문서의 시작으로 이동.
    "BottomOfFile": 3,   # 문서의 끝으로 이동.
    "TopOfList": 4,    # 현재 리스트의 시작으로 이동
    "BottomOfList": 5,   # 현재 리스트의 끝으로 이동
    "StartOfPara": 6,   # 현재 위치한 문단의 시작으로 이동
    "EndOfPara": 7,  # 현재 위치한 문단의 끝으로 이동
    "StartOfWord": 8,  # 현재 위치한 단어의 시작으로 이동.(현재 리스트만을 대상으로 동작한다.)
    "EndOfWord": 9,  # 현재 위치한 단어의 끝으로 이동.(현재 리스트만을 대상으로 동작한다.)
    "NextPara": 10, # 다음 문단의 시작으로 이동.(현재 리스트만을 대상으로 동작한다.)
    "PrevPara": 11, # 앞 문단의 끝으로 이동.(현재 리스트만을 대상으로 동작한다.)
    "NextPos": 12, # 한 글자 뒤로 이동.(서브 리스트를 옮겨 다닐 수 있다.)
    "PrevPos": 13, # 한 글자 앞으로 이동.(서브 리스트를 옮겨 다닐 수 있다.)
    "NextPosEx": 14,  # 한 글자 뒤로 이동.(서브 리스트를 옮겨 다닐 수 있다. 머리말/꼬리말, 각주/미주, 글상자 포함.)
    "PrevPosEx": 15,   # 한 글자 앞으로 이동.(서브 리스트를 옮겨 다닐 수 있다. 머리말/꼬리말, 각주/미주, 글상자 포함.)
    "NextChar": 16,  # 한 글자 뒤로 이동.(현재 리스트만을 대상으로 동작한다.)
    "PrevChar": 17,  # 한 글자 앞으로 이동.(현재 리스트만을 대상으로 동작한다.)
    "NextWord": 18, # 한 단어 뒤로 이동.(현재 리스트만을 대상으로 동작한다.)
    "PrevWord": 19, # 한 단어 앞으로 이동.(현재 리스트만을 대상으로 동작한다.)
    "NextLine": 20, # 한 줄 아래로 이동.
    "PrevLine": 21, # 한 줄 위로 이동.
    "StartOfLine": 22, # 현재 위치한 줄의 시작으로 이동.
    "EndOfLine": 23,  # 현재 위치한 줄의 끝으로 이동.
    "ParentList": 24, # 한 레벨 상위로 이동한다.
    "TopLevelList": 25, # 탑레벨 리스트로 이동한다.
    "RootList": 26, # 루트 리스트로 이동한다. 현재 루트 리스트에 위치해 있어 더 이상 상위 리스트가 없을 때는 위치 이동 없이 반환한다. 이동한 후의 위치는 상위 리스트에서 서브리스트가 속한 컨트롤 코드가 위치한 곳이다. 위치 이동시 셀렉션은 무조건 풀린다.
    "CurrentCaret": 27, # 현재 캐럿이 위치한 곳으로 이동한다. (캐럿 위치가 뷰의 맨 위쪽으로 올라간다. )
    "LeftOfCell": 100,  # 현재 캐럿이 위치한 셀의 왼쪽
    "RightOfCell": 101,  # 현재 캐럿이 위치한 셀의 오른쪽
    "UpOfCell": 102,  # 현재 캐럿이 위치한 셀의 위쪽
    "DownOfCell": 103,  # 현재 캐럿이 위치한 셀의 아래쪽
    "StartOfCell": 104, # 현재 캐럿이 위치한 셀에서 행(row)의 시작
    "EndOfCell": 105, # 현재 캐럿이 위치한 셀에서 행(row)의 끝
    "TopOfCell": 106, # 현재 캐럿이 위치한 셀에서 열(column)의 시작
    "BottomOfCell": 107, #현재 캐럿이 위치한 셀에서 열(column)의 끝
    "ScrPos": 200, # 한/글 문서장에서의 screen 좌표로서 위치를 설정 한다.
    "ScanPos": 201, # GetText() 실행 후 위치로 이동한다.
}

@patch
def move(app:App, move_key="ScanPos", para=None, pos=None):
    """키워드를 바탕으로 캐럿 위치를 이동시킵니다."""
    
    move_id = get_value(move_ids, move_key)
    return app.api.MovePos(moveID=move_id, Para=para, pos=pos)
    

# %% ../nbs/02_api/00_core.ipynb 29
size_options = {
    "realSize": 0,   # 이미지를 원래의 크기로 삽입한다.
    "specificSize": 1,    # width와 height에 지정한 크기로 그림을 삽입한다.
    "cellSize": 2,    # 현재 캐럿이 표의 셀안에 있을 경우, 셀의 크기에 맞게 자동 조정하여 삽입한다. 
    "cellSizeWithSameRatio":3    # 현재 캐럿이 표의 셀 안에 있을 경우, 셀의 크기에 맞추어 원본 이미지의 가로 세로 비율이 동일하게 확대/축소하여 삽입한다.
}

effects = {
    "RealPicture": 0,   # 원본
    "GrayScale": 1,    # 그레이 스케일
    "BlackWhite": 2,     # 흑백효과
}

@patch
def insert_picture(
    app:App,    # app
    fpath,     # 그림 위치
    width=None,     # 넓이
    height=None,     # 높이
    size_option="realSize",    # 사이즈 옵션 
    reverse=False,     # 이미지 반전 여부
    watermark=False,     # 워커마크 여부
    effect="RealPicture"    # 화면 효과
):
    """
    사이즈를 지정하여 사진 삽입
    """
    path = Path(fpath)
    sizeoption = get_value(size_options, size_option)
    effect = get_value(effects, effect)
    return app.api.InsertPicture(
        path.absolute().as_posix(), 
        Width=width, 
        Height=height, 
        sizeoption=sizeoption,
        reverse=reverse,
        watermark=watermark,
        effect=effect
    )

# %% ../nbs/02_api/00_core.ipynb 30
@patch
def select_text(app:App, option:str="Line"):
    """
    한줄을 선택합니다.
    """
    select_options  = {
        "Doc" : (app.actions.MoveDocBegin, app.actions.MoveSelDocEnd),
        "Para" : (app.actions.MoveParaBegin, app.actions.MoveSelParaEnd),
        "Line" : (app.actions.MoveLineBegin, app.actions.MoveSelLineEnd),
        "Word" : (app.actions.MoveWordBegin, app.actions.MoveSelWordEnd),
    }
    begin, end = select_options.get(option)
    return begin().run(), end().run()
    


# %% ../nbs/02_api/00_core.ipynb 33
@patch
def get_selected_text(app:App):
    """
    선택된 영역의 텍스트를 불러온다.
    """
    with app.scan(selection=True) as scan:
        text = "\n".join(scan)
    return text


# %% ../nbs/02_api/00_core.ipynb 35
@patch
def get_text(app:App, spos="Line", epos="Line"):
    """
    텍스트를 가져옵니다. 기본은 현재 문장입니다.
    """
    with app.scan(scan_spos=spos, scan_epos=epos) as txts:
        text = "".join(txts)
    return text


# %% ../nbs/02_api/00_core.ipynb 37
directions = {
    "Forward": 0,
    "Backward": 1, 
    "All": 2
}

# %% ../nbs/02_api/00_core.ipynb 38
@patch
def find_text(app:App, 
    text = "",
    text_fontcolor=None,  # 찾을 폰트 색
    fontsize=None,   # 찾을 폰트 크기(height)
    fontname="",  # 찾을 글꼴
    fonttype=1,   # 찾을 글꼴 타입 TTF = 1, HTF = 2
    fontratio=None,  # 찾을 장평
    spacing=None,  # 찾을 자간
    bold=None,  # 찾을 볼드
    italic=None, # 찾을 이텔릭
    underline=None,  # 찾을 밑줄
    strike_out=None,  # 찾을 취소선
    ignore_message=True,  # 메시지 무시 여부
    direction="Forward",   # 찾을 방향
    match_case=False,  # 대소문자 구분
    all_word_forms=False,  # 문자열 결합
    several_words=False,    #  여러 단어 찾기
    use_wild_cards=False,    # 아무개 문자
    whole_word_only=False,    # 온전한 낱말
    replace_mode=False,    # 찾아 바꾸기 모드
    ignore_find_string=False,    # 찾을 문자열 무시
    ignore_replace_string=False,    # 바꿀 문자열 무시
    find_style="",    # 찾을 스타일
    replace_style="",  
    find_jaso=False,    # 자소로 찾기
    find_reg_exp=False,    # 정규표현식으로 찾기
    find_type=False,    # 다시 찾기를 할 때 마지막으로 실한 찾기를 할 경우 True, 찾아가기를 할경우 False
    ):
    '''`text를 찾습니다.'''
    
    action = app.actions.RepeatFind()
    p = action.pset
    
    # set options
    p.FindString = text
    p.IgnoreMessage = ignore_message
    p.MatchCase = match_case
    p.AllWordForms = all_word_forms
    p.Direction = get_value(directions, direction)
    p.SeveralWords = several_words
    p.UseWildCards = use_wild_cards
    p.WholeWordOnly = whole_word_only
    p.ReplaceMode = replace_mode
    p.IgnoreFindString = ignore_find_string
    p.IgnoreReplaceString = ignore_replace_string
    p.FindStyle = find_style
    p.ReplaceStyle = replace_style
    p.FindJaso = find_jaso
    p.FindRegExp = find_reg_exp
    p.FindType = find_type

    # set old charshape
    set_charshape_pset(p.FindCharShape, face_name=fontname, font_type=fonttype, bold=bold, italic=italic, strike_out_type=strike_out, underline_type=underline, ratio=fontratio, spacing=spacing)
        
    return action.run()

# %% ../nbs/02_api/00_core.ipynb 40
@patch
def replace_all(app:App, 
                old = "",
                new = "",
                old_fontcolor=None,  # 찾을 폰트 색
                new_fontcolor=None,  # 바꿀 폰트 색
                old_fontsize=None,   # 찾을 폰트 크기(height)
                new_fontsize=None,   # 바꿀 폰트 크기(height)
                old_fontname="",  # 찾을 글꼴
                old_fonttype=1,   # 찾을 글꼴 타입 TTF = 1, HTF = 2
                new_fontname="",  # 바꿀 글꼴 
                new_fonttype=1,   # 바꿀 글꼴 타입 TTF = 1, HTF = 2
                old_fontratio=None,  # 찾을 장평
                new_fontratio=None,  # 바꿀 장평
                old_spacing=None,  # 찾을 자간
                new_spacing=None,  # 바꿀 자간
                old_bold=None,  # 찾을 볼드
                new_bold=None,  # 바꿀 볼드
                old_italic=None, # 찾을 이텔릭
                new_italic=None,  # 바꿀 이텔릭
                old_underline=None,  # 찾을 밑줄
                new_underline=None,  # 바꿀 밑줄
                old_strike_out=None,  # 찾을 취소선
                new_strike_out=None,  # 바꿀 취소선
                ignore_message=True,  # 메시지 무시 여부
                direction="All",   # 찾을 방향
                match_case=False,  # 대소문자 구분
                all_word_forms=False,  # 문자열 결합
                several_words=False,    #  여러 단어 찾기
                use_wild_cards=False,    # 아무개 문자
                whole_word_only=False,    # 온전한 낱말
                auto_spell=True,   # 토시 자동 교정
                replace_mode=True,    # 찾아 바꾸기 모드
                ignore_find_string=False,    # 찾을 문자열 무시
                ignore_replace_string=False,    # 바꿀 문자열 무시
                find_style="",    # 찾을 스타일
                replace_style="",    # 바꿀 스타일
                find_jaso=False,    # 자소로 찾기
                find_reg_exp=False,    # 정규표현식으로 찾기
                find_type=True,    # 다시 찾기를 할 때 마지막으로 실한 찾기를 할 경우 True, 찾아가기를 할경우 False
               ):
    
    action = app.actions.AllReplace()
    p = action.pset
    
    # set options
    p.FindString = old
    p.ReplaceString = new
    p.IgnoreMessage = ignore_message
    p.MatchCase = match_case
    p.AllWordForms = all_word_forms
    p.Direction = get_value(directions, direction)
    p.SeveralWords = several_words
    p.UseWildCards = use_wild_cards
    p.WholeWordOnly = whole_word_only
    p.AutoSpell = auto_spell
    p.ReplaceMode = replace_mode
    p.IgnoreFindString = ignore_find_string
    p.IgnoreReplaceString = ignore_replace_string
    p.FindStyle = find_style
    p.ReplaceStyle = replace_style
    p.FindJaso = find_jaso
    p.FindRegExp = find_reg_exp
    p.FindType = find_type

    # set old charshape
    set_charshape_pset(p.FindCharShape, face_name=old_fontname, font_type=old_fonttype, bold=old_bold, italic=old_italic, strike_out_type=old_strike_out, underline_type=old_underline, ratio=old_fontratio, spacing=old_spacing)
    set_charshape_pset(p.ReplaceCharShape, face_name=new_fontname, font_type=new_fonttype, bold=new_bold, italic=new_italic, strike_out_type=new_strike_out, underline_type=new_underline, ratio=new_fontratio, spacing=new_spacing)
        
    return action.run()
    

# %% ../nbs/02_api/00_core.ipynb 43
@patch
def insert_file(app:App, fpath, keep_charshape=False, keep_parashape=False, keep_section=False, keep_style=False):
    """
    파일 끼워 넣기
    """
    
    action = app.actions.InsertFile()
    p = action.pset
    p.filename= Path(fpath).absolute().as_posix()
    p.KeepCharshape = keep_charshape
    p.KeepParashape = keep_parashape
    p.KeepSection = keep_section
    p.KeepStyle = keep_style
    
    return action.run()
